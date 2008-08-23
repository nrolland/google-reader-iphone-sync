#import "Feeds2AppDelegate.h"
#import "tcWebView.h"
#import "tcHelpers.h"

@implementation Feeds2AppDelegate

@synthesize window;

- (void) applicationWillTerminate:(id) sender {
	dbg(@"teminating...");
	[appSettings dealloc];
	[db dealloc];
}

- (id) settings { return appSettings; }

- (void)applicationDidFinishLaunching:(UIApplication *)application {
	#ifndef DEBUG
		// redirect stderr to a logfile if we're not in debugging mode
		NSString *logPath = [[[self settings] docsPath] stringByAppendingPathComponent: @"GRiS.native.log"];
		freopen([logPath fileSystemRepresentation], "w", stderr);
	#endif
	dbg(@"Loaded...");

	[window setBackgroundColor: [UIColor groupTableViewBackgroundColor]];
	[self loadFirstView];
}

- (void) loadItemAtIndex: (int) index fromSet:(id) items {
	//dbg(@"appdelegate - loading item at index: %d from set %@", index, items);
	[[browseController webView] loadItemAtIndex: index fromSet:items];
	[self showViewer:self];
}

- (void)showNavigation: (id) sender {
	dbg(@"Navigation!");
	[[browseController webView] showCurrentItemInItemList: [mainController itemList]];
	[browseController deactivate];
	inItemViewMode = NO;
	[mainController activate];
}

- (void)showViewer: (id) sender {
	dbg(@"Viewer!");
	[mainController deactivate];
	inItemViewMode = YES;
	[browseController activate];
}

- (void)dealloc {
	[window release];
	[browseController release];
	[super dealloc];
}

- (void) loadFirstView {
	NSString * itemID = [appSettings getLastViewedItem];
	dbg(@"last viewed item = %@", itemID);
	[self showNavigation: self];
	if(!(itemID == nil || [itemID length] == 0)) {
		[itemListDelegate loadItemWithID:itemID];
	}
}


- (NSString *) currentItemID {
	NSString * itemID = nil;
	if(inItemViewMode) {
		dbg(@"item view is currently active");
		itemID = [browseController currentItemID];
	}
	return itemID;
}

@end

