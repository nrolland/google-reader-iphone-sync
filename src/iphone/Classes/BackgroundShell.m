#import "BackgroundShell.h"
#import <signal.h>

#define dbg NSLog

static FILE * my_popen (char * command, const char * type, pid * tid);

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
	// kill the worker thread:
	if(killpg(shellPid, SIGTERM) != 0) {
		dbg(@"Cancel failed to kill pid %d", shellPid);
	}
	wait(NULL);
}

- (FILE *) startCommand {
	FILE * proc;
	if(command == nil) {
		NSLog(@"command is nil. did you try to run it twice?");
		return NULL;
	}
	NSLog(@"BGShell: running command.");
	proc = my_popen([command cStringUsingEncoding:NSUTF8StringEncoding],"r", &shellPid);
	[command release];
	command = nil;
	return proc;
}



#import <sys/select.h>
#import <sys/time.h>
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
		return YES;
	}
	return NO; // still more to go
}
@end




// modified from: http://www.tek-tips.com/viewthread.cfm?qid=1373233&page=6
static FILE * my_popen (char * command, const char * type, pid * tid){
	int     p[2];
	FILE *  fp;

	if (*type != 'r' && *type != 'w')
		return NULL;

	if (pipe(p) < 0)
		return NULL;

	if ((*tid = fork()) > 0) { /* then we are the parent */
		if (*type == 'r') {
			close(p[1]);
			fp = fdopen(p[0], type);
		} else {
			close(p[0]);
			fp = fdopen(p[1], type);
		}
		/* make child thread id the process group leader */
		setpgid(*tid, *tid);
		//NSLog(@"parent: my pid is %d, the childs pid is %d and MY groupID is %d and the child's is %d", getpid(), *tid, getpgrp(), getpgid(*tid));
		return fp;
	} else if (*tid == 0) {  /* we're the child */
		
		if (*type == 'r') {
			fflush(stdout);
			fflush(stderr);
			close(1);
			if (dup(p[1]) < 0)
				perror("dup of write side of pipe failed");
			close(2);
			if (dup(p[1]) < 0)
			perror("dup of write side of pipe failed");
		} else {
			close(0);
			if (dup(p[0]) < 0)
				perror("dup of read side of pipe failed");
		}

		close(p[0]); /* close since we dup()'ed what we needed */
		close(p[1]);
		system(command);
		_exit(0);
	} else {		   /* we're having major problems... */
		close(p[0]);
		close(p[1]);
		printf("my_popen(): fork() failure!\n");
	}
	return NULL;
}