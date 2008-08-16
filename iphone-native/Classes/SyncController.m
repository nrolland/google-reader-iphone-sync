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
			
	NSString * shellString = [NSString stringWithFormat:@"python '%@' --no-html --show-status --flush-output --quiet --output-path='%@' --num-items='%d' --user='%@' --password='%@' %@ 2>&1",
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
	[cancelButton setHidden:YES];
	[okButton setHidden:YES];
	// now swap out the views
	[syncStatusView setHidden:NO];
	[window addSubview: syncStatusView];
	[syncStatusView setAlpha: 1.0];
	[syncStatusView setFrame: [window frame]];
	[status_currentTask setText: @"Loading..."];
	[status_mainProgress setProgress: 0.0];
	[status_taskProgress setProgress: 0.0];
	[status_taskProgress setHidden:NO];
	[status_mainProgress setHidden:NO];
	
	// animate!
	[syncStatusView animateFadeIn];

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

- (void) syncViewIsGone{
	[syncStatusView setHidden:YES];
	[syncStatusView removeFromSuperview];
}

- (IBAction) hideSyncView: (id)sender {
	[syncStatusView animateFadeOutThenTell:self withSelector:@selector(syncViewIsGone)];
	[db reload];
	[itemsController refresh:self];
}

// sync finished but you still want to see the report
- (void) showSyncFinished {
	[status_taskProgress setHidden:YES];
	[status_mainProgress setHidden:YES];

	[spinner setHidden:YES];
	[okButton setHidden:NO];
	[cancelButton setHidden:YES];
}

#pragma mark delegate callbacks
- (void) backgroundShell:(id)shell didFinishWithSuccess:(BOOL) success {
	if(!success) {
		dbg(@"failed...");
		[status_currentTask setText:@"Sync aborted"];
	} else {
		dbg(@"sync completed successfully");
		[status_currentTask setText:@"Sync complete"];
	}
	[syncThread release];
	syncThread = nil;
	[self showSyncFinished];
}

- (void) backgroundShell:(id)shell didProduceOutput:(NSString *) line {
	dbg(@"sync output: %@", line);
	int numStatusComponents;

	if([line hasPrefix:@"STAT:"]){
		NSArray * statusComponents = [line componentsSeparatedByString:@":"];
		numStatusComponents = [statusComponents count];
		if(numStatusComponents > 1) {
			@try{
				NSString * type = [statusComponents objectAtIndex:1];
				if(       [type isEqualToString:@"TASK_TOTAL"]){
					// total number of tasks
					totalTasks = [[statusComponents objectAtIndex:2] integerValue];
				} else if([type isEqualToString:@"TASK_PROGRESS"]){
					// new sub-task, with optional description
					if(numStatusComponents > 3) {
						[status_currentTask setText: [statusComponents objectAtIndex:3]];
					}
					[status_mainProgress setProgress: ([[statusComponents objectAtIndex:2] floatValue] / (float)totalTasks )];
					[status_taskProgress setProgress: 0.0];
				} else if([type isEqualToString:@"SUBTASK_TOTAL"]){
					// total number of steps for current subtask
					totalStepsInCurrentTask = [[statusComponents objectAtIndex:2] integerValue];
				} else if([type isEqualToString:@"SUBTASK_PROGRESS"]){
					// progress for current subtask
					[status_taskProgress setProgress: ( [[statusComponents objectAtIndex:2] floatValue] / (float)totalStepsInCurrentTask ) ];
				} else {
					dbg(@"unknown status type: %@", type);
				}
			} @catch(NSException *e) {
				dbg(@"error occurred:\n%@", e);
			}
		}
	}
}

@end
