#import <Foundation/Foundation.h>

typedef long pid;

@interface BackgroundShell : NSThread {
	id delegate;
	NSString * command;
	float secondsPerLoop;
	BOOL doSendOutput;
	SEL outputCallback;
	id outputDelegate;
	pid shellPid;
}

- (id) initWithShellCommand:(NSString *)cmd;
- (void) setPollTime: (float) pollTimeInSeconds;
- (void) setDelegate: del;
@end
