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
$rsync_opts = "--recursive --delete --progress --checksum"

$remote_mac_path = "#{$mac_user}@#{$mac_server}:#{$mac_path}"
$remote_ipod_path = "#{$ipod_user}@#{$ipod_server}:#{$ipod_path}"

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
	run "rsync #{$rsync_opts} #{$remote_mac_path} #{$ipod_path}"
end

task :pull_without_web do
	check_folder($mac_path)
	run "rsync #{$rsync_opts} #{$ipod_path} #{$remote_mac_path}"
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
	run "rsync #{$rsync_opts} --exclude='*.psd' #{$remote_mac_path}/../template #{$ipod_path}/../"
end

task :lighttpd do
	dest_dir = '/var/mobile/Media/.dirlist/'
	current_dir = `pwd`.chomp!
	src = "#{$mac_user}@#{$mac_server}:#{current_dir}/lighttpd"
	run "rsync --recursive --progress --checksum --exclude='.*' '#{src}/dirlist/' '#{dest_dir}'"
	run "rsync --progress --checksum --exclude='.*' '#{src}/lighttpd.conf' '/usr/local/etc/lighttpd.conf'"
end

desc "install required files on your iPod / iPhone"
task :install do
	lighttpd
	push_template
	run("mkdir -p '#{$ipod_path}'")
	puts "All set up!"
end



# make sure that folder is empty, aside from files matching allowed_patterns
# (when it's a remote directory, it only ensures the directory exists)
def check_folder(path, remote = false)
	cmd = "mkdir -p \"#{path}\""
	if remote
		run(cmd)
	else
		system(cmd)
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

def do_sync(*opts)
	return if $dry
	synced = system "./src/main.py #{opts.join(' ')} #{$app_opts.join(' ')}"
	puts "*** Sync failed ***" unless synced
end

def loud_error(err)
	raise <<-EOF

#{'*' * 80}
#{err}
#{'*' * 80}
EOF
end
