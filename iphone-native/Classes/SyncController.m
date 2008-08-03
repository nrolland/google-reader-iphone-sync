#import "SyncController.h"
#import "tcHelpers.h"
#import <stdio.h>

@implementation SyncController

- (IBAction) sync: (id) sender {
	dbg(@"syncing!");
	if(syncThread && ![syncThread isFinished]) {
		dbg(@"thread is still running!");
		return;
	}
	
	id settings = [[[UIApplication sharedApplication] delegate] settings];
	NSString * shellString = [NSString stringWithFormat:@"python '%@' --test --num-items='%d' --user='%@' --pass='%@' 2>&1",
		[[settings docsPath] stringByAppendingPathComponent:@"src/main.py"],
		[settings itemsPerFeed],
		[settings email],
		[settings password]];
	syncThread = [[BackgroundShell alloc] initWithShellCommand: shellString];
	[syncThread setDelegate: self];
	[syncThread start];

	// visuals
	[spinner setAnimating:YES];
	[downloadProgrssBar setProgress:0.0];
	[cancelButton setHidden:NO];
	[okButton setHidden:YES];
	// now swap out the views
	[notSyncingView setHidden:YES];
	[syncStatusView setHidden:NO];
	[window addSubview: syncStatusView];

	// ..and go!
	[syncThread start];
}

- (IBAction) cancelSync: (id) sender {
	if(!syncThread || [syncThread isFinished]) {
		dbg(@"can't cancel - it's already finished!");
		return;
	}
	NSLog(@"cancelling thread...");
	[syncThread cancel];

	// visuals
	[syncStatusView removeFromSuperView];
	[notSyncingView setHidden:NO];
	[[self tabBarItem] setBadgeValue: nil];
}

#pragma mark delegate callbacks
- (void) backgroundShell:(id)shell didFinishWithSuccess:(BOOL) success {
	if(!success) {
		dbg(@"failed...");
	} else {
		dbg(@"sync completed successfully");
	}
	[syncThread release];
	syncThread = nil;
}

- (void) backgroundShell:(id)shell didProduceOutput:(NSString *) line {
	dbg(@"SyncController got the output: %@", line);
	[runningOutput setText: line];
}

@end
