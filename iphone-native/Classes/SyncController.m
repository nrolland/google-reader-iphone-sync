#import "SyncController.h"
#import "tcHelpers.h"

@implementation SyncController

- (IBAction) sync: (id) sender {
	dbg(@"syncing!");
	[spinner setAnimating:YES];
	[downloadProgrssBar setProgress:0.0];

	// now swap out the views
	[notSyncingView setHidden:YES];
	[syncStatusView setHidden:NO];
	[[self tabBarItem] setBadgeValue: @" "];
}

- (IBAction) cancelSync: (id) sender {
	[syncStatusView setHidden:YES];
	[spinner setAnimating:NO];
	[notSyncingView setHidden:NO];
	[[self tabBarItem] setBadgeValue: nil];
}

@end
