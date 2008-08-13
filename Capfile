require 'YAML'

config_filename = 'config.yml'
config = YAML.load_file(config_filename)
# sanity-check
missing_items = ['iphone_user','iphone_destination_path', 'iphone_hostname'].select{ |item| not (config.has_key?(item)) }
raise "You need to specify #{missing_itemsjoin(", ")} in #{config_filename}" unless missing_items.empty?


$ipod_user = config['iphone_user']
set :user, $ipod_user
set :password, config['iphone_password'] if config['iphone_password']

$mac_user = config['mac_user'] || `whoami`.chomp!
$mac_server = `hostname`.chomp!

# servers & paths
$ipod_path = "/var/mobile/GRiS/"

$ipod_server = ENV['IP'] || config['iphone_hostname']
puts "IP = #{ENV['IP'].inspect}"
puts "HOSNTAME = #{config['iphone_hostname'].inspect}"
puts "SERVER = #{$ipod_server.inspect}"

role :ipod, $ipod_server

# general options
$rsync_opts = "--recursive --delete --checksum --progress --copy-links"

$remote_mac_path = "#{$mac_user}@#{$mac_server}:#{$mac_path}"
$remote_ipod_path = "#{$ipod_user}@#{$ipod_server}:#{$ipod_path}"
$remote_ipod = "#{$ipod_user}@#{$ipod_server}:"

$run_opts = {}

# -----------------------------------------
# application options
$app_opts = []

desc "set CAUTIOUS mode on"
task :carefully do $app_opts << '--cautious' end

desc "set VERBOSE mode on"
task :loudly do $app_opts << '--verbose' end

$dry = false
desc "use --dry-run only (no actual filesystem changes)"
task :fake do $dry = true; $rsync_opts += " --dry-run" end
# -----------------------------------------

desc "flush the dns cache"
task :dns do `sudo dscacheutil -flushcache` end

desc "test the source code with nosetest"
task :nose do
	if ENV['file']
		where = ENV['file']
	else
		puts " (add file=src/<module>.py to test a single module)"
		where = '--where=src'
	end
	system("nosetests -c nose.cfg #{where}")
end

$only_one = true
task :many do $only_one = false end

desc "run a web-sync in test mode"
task :t do
	opts = ['--test']
	opts << '--num-items=1' if $only_one
	do_sync(opts.join(" "))
end

desc "pause between steps"
task :pause do $run_opts[:pause] = true end

desc "Copy the template files (buttons, styles) to iPod"
task :push_template do
	local "rsync #{$rsync_opts} --exclude='*.psd' 'template' '#{$remote_ipod_path}'"
end

desc "copy python code to iPod"
task :push_python_code do
	local "rsync #{$rsync_opts} --exclude='*.psd' 'src' '#{$remote_ipod_path}'"
end

desc "copy ~/.ssh/id_rsa.pub to ipod / iphone"
task :ssh_auth do
	upload '~/.ssh/id_rsa.pub', "~/.ssh_id_#{$mac_user}"
	run "cat '~/.ssh_id_#{$mac_user}' >> '~/.ssh/authorrized_keys'"
end


# installing & running the code on your iPhone
desc "build & install code on iPod"
task :install do
		install_app
		push_python_code
end

desc "build the native iPhone version"
task :build do
	local "xcodebuild -project iphone-native/GRiS.xcodeproj -configuration #{ENV['build'] || "Release"}"
end

desc "create a cydia package"
task :package do
	build
	do_package
end

build_dir = "GRiS.pkg-build"
task :do_package do
	app = "GRiS"
	app_dir = "#{build_dir}/#{app}"

	local "rm -rf #{app_dir}"
	local "mkdir -p #{app_dir}"
	local "mkdir -p #{app_dir}/Applications"
	local "mkdir -p #{app_dir}/var/mobile/GRiS"
	local "mkdir -p #{app_dir}/DEBIAN"
	
	# sign the code
	# (man, this is hacky...)
	local "rsync #{$rsync_opts} iphone-native/build/Release-iphoneos/GRiS.app/GRiS #{$ipod_user}@#{$ipod_server}:/tmp"
	run "ldid -S /tmp/GRiS"
	local "rsync #{$rsync_opts} #{$ipod_user}@#{$ipod_server}:/tmp/GRiS iphone-native/build/Release-iphoneos/GRiS.app/"
	run "rm /tmp/GRiS"

	# file heirarchy
	local "cp -r iphone-native/build/Release-iphoneos/GRiS.app #{app_dir}/Applications/"
	local "cp -r template #{app_dir}/var/mobile/GRiS/"
	local "cp -r src #{app_dir}/var/mobile/GRiS/"

	# control file
	local "cp -r cydia/control #{build_dir}/#{app}/DEBIAN/"
	
	# package it up
	local "cd #{build_dir} && dpkg-deb -b #{app}"

	puts "-"*50
	
	if config['deb_dest']
		dest = config['deb_dest']
		local "cp '#{build_dir}/#{app}.deb' '#{dest}'"
		local "cd '#{dest}' && dpkg-scanpackages . /dev/null > Packages"
		local "cd '#{dest}' && gzip -c Packages > Packages.gz"
		puts "Package file: #{dest}/Packages.gz"
		puts "DEB file:     #{dest}/#{app}.deb"
		puts "all files:\n '#{dest}/Packages.gz' '#{dest}/Packages' '#{dest}/#{app}.deb'"
	else
		puts "set deb_dest in config.yml to generate a package file automatically"
		puts "DEB file:     #{build_dir}/#{app}.deb"
	end
end

task :clean do
	local "rm -rf #{build_dir}"
end

task :install_eggs do
	install_egg_file('PyYAML-3.05-py2.5.egg')
end

task :install_app do
	build
	run "mkdir -p /var/mobile/GRiS"
	# sync it
	local "rsync #{$rsync_opts} iphone-native/build/Release-iphoneos/GRiS.app #{$ipod_user}@#{$ipod_server}:/Applications/"
	local "rsync #{$rsync_opts} src #{$ipod_user}@#{$ipod_server}:#{$settings_path}"
	push_template
	#	local "rsync #{$rsync_opts} --exclude '*.sqlite' --exclude '*.plist' ~/.GRiS/ #{$ipod_user}@#{$ipod_server}:/var/mobile/GRiS/"
	run "ldid -S /Applications/GRiS.app/GRiS"
	run "chown -R mobile.mobile /var/mobile/GRiS/"
	run "killall SpringBoard"
end


def install_egg_file(file, location='eggs', force = false)
	path = location + '/' + file
	python_plugin_path = '/usr/lib/python2.5/site-packages/'
	# returning false (non-zero) from a remote shell throws an exception with capistrano.. so we'll use that:
	begin
		remote("test -d '#{python_plugin_path}#{File.basename(file,'.egg')}")
		raise "dummy" if force
	rescue
		system "scp '#{path}' '#{$ipod_user}@#{$ipod_server}:#{python_plugin_path}'" or loud_error("couldn't copy egg file: #{path}")
		run "cd '#{python_plugin_path}' && unzip -uo '#{file}' && rm '#{file}'"
	end
end


# ----------- helpers -------------

# make sure that folder is empty, aside from files matching allowed_patterns
# (when it's a remote directory, it only ensures the directory exists)
def check_folder(path, remote = false)
	cmd = "mkdir -p \"#{path}\""
	if remote
		run(cmd)
	else
		local(cmd)
		allowed_patterns = [/\.pdf$/, /\.pickle$/, /\.html$/,/^./]
		Dir[path + '/*'].each do |f|
#			puts f
			unless allowed_patterns.any? { |pattern| f =~ pattern }
				loud_error("ERROR: The destination folder contains non-generated files:\n#{path}\n" +
					"Please clean out this folder or pick a different destination folder in config.yml")
			end
		end
	end
end

def pause(desc = "something")
	if $run_opts[:pause]
		puts("About do #{desc}...")
		puts("  [press return to continue]")
		$stdin.gets
	end
end

def local(cmd, error_msg="Command Failed")
	puts "running locally:\n >#{cmd}"
	system(cmd) or loud_error("> #{cmd}\n#{error_msg}")
end

def do_sync(*opts)
	return if $dry
	synced = system "./src/main.py #{opts.join(' ')} #{$app_opts.join(' ')}"
	puts "*** Sync failed ***" unless synced
end

def local(cmd, error=nil)
	error = "command failed: #{cmd}" if error.nil?
	system(cmd) or loud_error(error)
end

def loud_error(err)
	raise <<-EOF

#{'*' * 80}
#{err}
#{'*' * 80}
EOF
end
