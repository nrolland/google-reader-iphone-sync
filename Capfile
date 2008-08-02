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
$ipod_path = '/var/mobile/Media/' + config['iphone_destination_path']
$mac_path	= `pwd`.chomp! + "/entries/"

$ipod_server = ENV['IP'] || config['iphone_hostname']
puts "IP = #{ENV['IP'].inspect}"
puts "HOSNTAME = #{config['iphone_hostname'].inspect}"
puts "SERVER = #{$ipod_server.inspect}"

role :ipod, $ipod_server

# general options
$rsync_opts = "--recursive --delete --checksum --progress --links"

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

desc "Copy files to iPod"
task :push do
	check_folder($ipod_path, true)
	local "rsync #{$rsync_opts} #{$mac_path} #{$remote_ipod_path}"
end

task :pull_without_web do
	check_folder($mac_path)
	local "rsync #{$rsync_opts} #{$remote_ipod_path} #{$mac_path}"
end

desc "Copy files from iPod"
task :pull do pull_without_web ; pause("push read items info to google"); push_web end

desc "sync to the web (mark as read; get new items)"
task :sync_web do do_sync end

desc "just mark-as-read on the web (don't download new stuff)"
task :push_web do do_sync('--no-download') end
	
desc "update templates on downloaded items"
task :template do do_sync('--template') end
	
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

desc "Do a full sync"
task :all do pull_without_web; pause("sync with google"); sync_web; pause("push files to ipod"); push; push_template end

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
	check_folder($ipod_path + '/../', true)
	local "rsync #{$rsync_opts} --exclude='*.psd' '#{$mac_path}/../template' '#{$remote_ipod_path}/../'"
end

desc "copy ~/.ssh/id_rsa.pub to ipod / iphone"
task :ssh_auth do
	upload '~/.ssh/id_rsa.pub', "~/.ssh_id_#{$mac_user}"
	run "cat '~/.ssh_id_#{$mac_user}' >> '~/.ssh/authorrized_keys'"
end

task :lighttpd do
	check_folder('/var/mobile/Media/.dirlist/', true)
	check_folder('/usr/local/etc/', true)
	dest_dir = "#{$remote_ipod}/var/mobile/Media/.dirlist/"
	current_dir = `pwd`.chomp!
	src = "#{current_dir}/lighttpd"
	local "rsync #{$rsync_opts} '#{src}/dirlist/' '#{dest_dir}'"
	local "rsync #{$rsync_opts} '#{src}/lighttpd.conf' '#{$remote_ipod}/usr/local/etc/'"
	local "rsync #{$rsync_opts} '#{src}/com.sysprosoft.gfxmonk.lighttpd.startup.plist' '#{$remote_ipod}/System/Library/LaunchDaemons/'"
end

desc "install required files on your iPod / iPhone"
task :install do
	lighttpd
	push_template
	run("mkdir -p '#{$ipod_path}'")
	puts "All set up!"
end


# installing & running the code on your iPhone
desc "install code on iPod"
task :install_code do
		install_eggs
		update_code
end

desc "crate .app package"
task :make_app do
	# put code in app bundle
	local "mkdir -p GRiS.app"
	local "cp -R app_contents/* GRiS.app"
	local "cp -R src GRiS.app/"
	local "cp config.yml GRiS.app/"
end

desc "update ipod code"
task :update_code do
	make_app
	# sync it
	local "rsync #{$rsync_opts} iphone-native/GRiS.app #{$ipod_user}@#{$ipod_server}:/Applications/"
end

def install_egg_file(file, location='eggs')
	path = location + '/' + file
	python_plugin_path = '/usr/lib/python2.5/site-packages/'
	system "scp '#{path}' '#{$ipod_user}@#{$ipod_server}:#{python_plugin_path}'" or loud_error("couldn't copy egg file: #{path}")
	run "cd '#{python_plugin_path}' && unzip -uo '#{file}' && rm '#{file}'"
end

task :install_eggs do
	install_egg_file('PyYAML-3.05-py2.5.egg')
end

task :run_remotely do
	run "cd #{$ipod_path} && src/main.py"
end



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
