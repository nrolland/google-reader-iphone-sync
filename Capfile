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

$branch = `git-branch | grep '^\\*' | cut -b 3-`.chomp
$deploy_branches = ['master', 'iphone-native']

# servers & paths
$ipod_path = "/var/mobile/GRiS/"

ipod_ip = ENV['ip']
ipod_ip = "192.168.1.#{ipod_ip}" if ipod_ip =~ /^[0-9]+$/ # shortcut
# puts "IP = #{ipod_ip.inspect}"
# puts "HOSNTAME = #{config['iphone_hostname'].inspect}"
# puts "SERVER = #{$ipod_server.inspect}"

$ipod_server = ipod_ip || config['iphone_hostname']

role :ipod, $ipod_server

# general options
$rsync_opts = "--recursive --delete --checksum --progress --copy-links"

$remote_mac_path = "#{$mac_user}@#{$mac_server}:#{$mac_path}"
$remote_ipod_path = "#{$ipod_user}@#{$ipod_server}:#{$ipod_path}"
$remote_ipod = "#{$ipod_user}@#{$ipod_server}:"

$run_opts = {}

task :default do nose end

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
	packages = Dir['src/*.py'].collect {|p| p.gsub(/\.py$/i, '').gsub('/','.') }
	packages.reject! {|p| p =~ /__init__/ }
	puts "nosetests -c nose.cfg #{where} --cover-package='#{packages.join(',')}'"
	system("nosetests -c nose.cfg #{where} --cover-package='#{packages.join(',')}'")
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
build_dir = "GRiS.pkg-build"
app = "GRiS"
app_dir = "#{build_dir}/#{app}"

desc "build the native iPhone app"
task :build do
	icon_suffix = 'test'
	icon_suffix = 'release' if $deploy_branches.include? $branch
	system("cp iphone-native/Icon_#{icon_suffix}.png iphone-native/Icon.png") or puts "Couldn't copy Icon_#{icon_suffix}.png\n" + "-" * 80
	local "xcodebuild -project iphone-native/GRiS.xcodeproj -configuration #{ENV['build'] || "Release"}"
end

namespace :package do
	desc "create a cydia package"
	task :default do
		build
		do_package
	end

	task :install do
		default
		local "scp #{build_dir}/#{app}.deb #{$ipod_user}@#{$ipod_server}:/tmp"
		sudo "dpkg -i /tmp/#{app}.deb"
		run "rm /tmp/#{app}.deb"
#		sudo "killall SpringBoard"
	end

	task :build_repository do
		if config['deb_dest']
			dest = config['deb_dest']
			local "cp '#{build_dir}/#{app}.deb' '#{dest}'"
		
			# my dpkg-deb seems to be broken. I know not why, or how to fix it. So i run it though sed instead:
			local "cd '#{dest}' && dpkg-scanpackages . /dev/null | sed -e's/^name/Name/' -e's/^author/Author/' -e's/icon/Icon/' -e's/^homepage/Homepage/' > Packages"
		
			local "cd '#{dest}' && gzip -c Packages > Packages.gz"
			puts "Package file: #{dest}/Packages.gz"
			puts "DEB file:     #{dest}/#{app}.deb"
			puts "all files:\n '#{dest}/Packages.gz' '#{dest}/Packages' '#{dest}/#{app}.deb'"
		else
			puts "set deb_dest in config.yml to generate a package file automatically"
			puts "DEB file:     #{build_dir}/#{app}.deb"
		end
	end

	task :code_sign do
		# sign the code
		# (man, this is hacky...)
		local "rsync #{$rsync_opts} iphone-native/build/Release-iphoneos/GRiS.app/GRiS #{$ipod_user}@#{$ipod_server}:/tmp"
		run "ldid -S /tmp/GRiS"
		local "rsync #{$rsync_opts} #{$ipod_user}@#{$ipod_server}:/tmp/GRiS iphone-native/build/Release-iphoneos/GRiS.app/"
		local "chmod +x iphone-native/build/Release-iphoneos/GRiS.app/GRiS"
		run "rm /tmp/GRiS"
	end

	task :do_package do
		local "rm -rf #{app_dir}"
		local "mkdir -p #{app_dir}"
		local "mkdir -p #{app_dir}/Applications"
		local "mkdir -p #{app_dir}/var/mobile/GRiS"
		local "mkdir -p #{app_dir}/DEBIAN"

		code_sign

		# file heirarchy
		local "cp -r iphone-native/build/Release-iphoneos/GRiS.app #{app_dir}/Applications/"
		local "cp -r template #{app_dir}/var/mobile/GRiS/"
		local "cp -r src #{app_dir}/var/mobile/GRiS/"
		
		version = `grep -i '^Version' cydia/control`.chomp.split[-1].split('-')[0]
		puts "version: #{version}"
		local "echo '#{version}' > #{app_dir}/var/mobile/GRiS/VERSION"

		# control file, install scripts
		local "cp -r cydia/* #{build_dir}/#{app}/DEBIAN/"
	
		# package it up
		local "cd #{build_dir} && export COPY_EXTENDED_ATTRIBUTES_DISABLE=1 && dpkg-deb -b #{app}"

		puts "-"*50
		build_repository

	end

	task :clean do
		local "rm -rf #{build_dir}"
	end
end

# ----------- helpers -------------

def pause(desc = " (do something)")
	if $run_opts[:pause]
		puts("About to #{desc}...")
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

task :clean do
	`rm -rf '#{build_dir}'`
end

task :end do
	`growlnotify -m 'Completed' 'capistrano task'`
	clean
end