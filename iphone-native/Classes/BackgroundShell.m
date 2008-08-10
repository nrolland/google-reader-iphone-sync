#import "BackgroundShell.h"

#define dbg NSLog

@implementation BackgroundShell

- (id) initWithShellCommand:(NSString *)cmd {
	self = [super init];
	command = [cmd copy];
	[self setPollTime: 0.5];
	doSendOutput = NO;
	return self;
}

- (void) setPollTime: (float) pollTimeInSeconds {
	secondsPerLoop = pollTimeInSeconds;
}

- (void) setDelegate: del {
	[delegate release];
	delegate = [del retain];
	doSendOutput = [delegate respondsToSelector:@selector(backgroundShell:didProduceOutput:)];
}


#pragma mark callback methods that run in and communicate with other objects in the main thread
- (void) notifyOfOutput: (id) output {
	if(doSendOutput) {
		[delegate backgroundShell:self didProduceOutput:output];
	}
}

- (void) notifyOfCompletion:(NSNumber *) boolSuccess {
	if([delegate respondsToSelector:@selector(backgroundShell:didFinishWithSuccess:)]) {
		[delegate backgroundShell:self didFinishWithSuccess:[boolSuccess boolValue]];
	}
}

#pragma mark the main polling loop
- (void) main {
	NSAutoreleasePool * pool = [[NSAutoreleasePool alloc] init];
	FILE *proc = [self startCommand];
	BOOL success;
	if(proc == NULL) {
		NSLog("popen failed!");
		success = false;
	} else {
		while(![self command:proc hasFinishedWithSuccess:&success]) {
			[pool drain];
			// and make a new one...
			pool = [[NSAutoreleasePool alloc] init];
		}
	}
	[self performSelectorOnMainThread:@selector(notifyOfCompletion:) withObject:[NSNumber numberWithBool:success] waitUntilDone:YES];
	[pool release];
}

- (void) cancel {
	[super cancel];
}

- (FILE *) startCommand {
	FILE * proc;
	if(command == nil) {
		NSLog(@"command is nil. did you try to run it twice?");
		return;
	}
	NSLog(@"running command: %@", command);
	proc = popen([command cStringUsingEncoding:NSASCIIStringEncoding],"r");
	[command release];
	command = nil;
	return proc;
}



#import <sys/select.h>
#import <sys/time.h>
// ugh, this is a fun one... we need to use select() to make sure we check the
// cancelled status at least twice a second
-(BOOL) command:(FILE *) proc hasFinishedWithSuccess:(BOOL *)success {
	char line[1024];
	int ready;
	struct timeval waitTime;
	waitTime.tv_sec = (int)secondsPerLoop;
	waitTime.tv_usec = (int)((secondsPerLoop - waitTime.tv_sec) * 1000000); // 1 million microseconds to a second
	int fd = fileno(proc); // get the file descriptor
	
	// create the file descriptor set
	fd_set read_fds;
	FD_ZERO(&read_fds);
	FD_SET(fd, &read_fds);
	
	ready = select(fd + 1, &read_fds, NULL, NULL, &waitTime);
	if(ready) {
		char *output = fgets(line, sizeof(line), proc);
		if(output) {
			if(doSendOutput) {
				[self performSelectorOnMainThread:@selector(notifyOfOutput:) withObject:[NSString stringWithCString: line encoding: NSASCIIStringEncoding] waitUntilDone:YES];
			}
		}
		if(feof(proc)) {
			*success = pclose(proc) == 0;
			return YES;
		}
	}
	
	if([[NSThread currentThread] isCancelled]) {
		*success = NO;
		// TODO: send SIGINT. might need to replace popen() with fork()/exec() etc... fun!
		return YES;
	}
	return NO; // still more to go
}
@end
