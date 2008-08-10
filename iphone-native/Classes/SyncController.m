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
	NSMutableString * tag_string = [NSMutableString string];
	for(NSString * tag in [settings tagListArray]) {
		dbg(@"tag = %@", tag);
		tag = [tag stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceCharacterSet]];
		if([tag length] > 0) {
			[tag_string appendFormat: @" --tag='%@'", [tag stringByReplacingOccurrencesOfString:@"'" withString:@"\\'"]];
		}
	}
	if([tag_string length] == 0){
		NSLog(@"no feeds! aborting...");
		[self showSyncFinished];
		return;
	}
			
	NSString * shellString = [NSString stringWithFormat:@"python '%@' --no-html --flush-output --quiet --output-path='%@' --num-items='%d' --user='%@' --password='%@' %@ 2>&1",
		[[settings docsPath] stringByAppendingPathComponent:@"src/main.py"],
		[settings docsPath],
		[settings itemsPerFeed],
		[settings email],
		[settings password],
		tag_string];
	syncThread = [[BackgroundShell alloc] initWithShellCommand: shellString];
	[syncThread setDelegate: self];

	// visuals
	[spinner setAnimating:YES];
	[spinner setHidden:NO];
	[downloadProgrssBar setProgress:0.0];
	[cancelButton setHidden:YES];
	[okButton setHidden:YES];
	// now swap out the views
	[notSyncingView setHidden:YES];
	[syncStatusView setHidden:NO];
	[window addSubview: syncStatusView];
	[syncStatusView setFrame: [window frame]];
	[runningOutput setText: @"starting up...\n"];

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
	[cancelButton setHidden:YES];
}

- (IBAction) hideSyncView: (id)sender {
	[runningOutput setText: nil];
	[notSyncingView setHidden:NO];
	[syncStatusView setHidden:YES];
	[syncStatusView removeFromSuperview];
	
	[db reload];
	[itemsController refresh:self];
}

// sync finished but you still want to see the report
- (void) showSyncFinished {
	[spinner setHidden:YES];
	[okButton setHidden:NO];
	[cancelButton setHidden:YES];
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
	[self showSyncFinished];
}

- (void) backgroundShell:(id)shell didProduceOutput:(NSString *) line {
	dbg(@"SyncController got the output: %@", line);
	//[runningOutput setText: line];
	[runningOutput setText: [[runningOutput text] stringByAppendingString: line]];
	[runningOutput scrollRangeToVisible: NSMakeRange([[runningOutput text] length],1)];
}

@end
