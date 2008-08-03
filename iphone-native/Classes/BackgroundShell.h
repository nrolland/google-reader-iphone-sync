#import <Foundation/Foundation.h>


@interface BackgroundShell : NSThread {
	id delegate;
	NSString * command;
	float secondsPerLoop;
	BOOL doSendOutput;
	SEL outputCallback;
	id outputDelegate;
}

- (id) initWithShellCommand:(NSString *)cmd;
- (void) setPollTime: (float) pollTimeInSeconds;
- (void) setDelegate: del;
@end
