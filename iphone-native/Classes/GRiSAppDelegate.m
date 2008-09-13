#import "GRiSAppDelegate.h"
#import "ItemView.h"
#import "TCHelpers.h"

@implementation GRiSAppDelegate

@synthesize window;

- (void) applicationWillTerminate:(id) sender {
	dbg(@"teminating...");
	[appSettings dealloc];
	[db dealloc];
}

- (id) settings { return appSettings; }
- (id) mainController { return mainController; }

- (void)applicationDidFinishLaunching:(UIApplication *)application {
	#ifndef SIMULATOR
		// redirect stderr to a logfile if we're not on the simulator
		NSString *logPath = [[[self settings] docsPath] stringByAppendingPathComponent: @"GRiS.native.log"];
		dbg(@"opening logfile at: %@", logPath);
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
	[self setViewToShowItem: NO];
	[mainController activate];
}

- (void) setViewToShowItem:(BOOL) showItemView {
	inItemViewMode = showItemView;
	if(showItemView) {
		[[mainController view] addSubview:[browseController view]];
		CGRect frame = [[mainController view] bounds];
		frame.origin = CGPointMake(0,0);
		[[browseController view] setFrame: frame];
	} else {
		[[browseController view] removeFromSuperview];
	}
	[[[mainController selectedViewController] navigationBar] setHidden: showItemView];
	[[mainController tabBar] setHidden: showItemView];
	[[mainController view] layoutSubviews];
}

- (void)showViewer: (id) sender {
	dbg(@"Viewer!");
	[mainController deactivate];
	[self setViewToShowItem: YES];
	[browseController activate];
}

- (IBAction) toggleOptions: (id) sender {
	UIView * currentView = [[[mainController navController] topViewController] view];
	id subviews = [currentView subviews];
	if([subviews containsObject: optionsView]) {
		dbg(@"hiding options");
		[optionsView removeFromSuperview];
		[[[mainController navController] topViewController] refresh: self];
	} else {
		dbg(@"showing options");
		[currentView addSubview: optionsView];
		[optionsView setHidden: NO];
		[optionsView animateFadeIn];
	}
}
- (id) currentListController {
	return [[mainController navController] topViewController];
}
- (IBAction) markItemsAsRead: (id) sender    { [self markItemsWithReadState: YES]; }
- (IBAction) markItemsAsUnread: (id) sender  { [self markItemsWithReadState: NO];  }

- (void) markItemsWithReadState: (BOOL) read {
	[[self currentListController] markItemsWithReadState:read];
	[self toggleOptions: self];
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
	[window addSubview:[mainController view]];
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

