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

- (BOOL) inItemViewMode { return inItemViewMode; }
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
	loading = YES;
	[self loadFirstView];
}

- (void) loadItemAtIndex: (int) index fromSet:(id) items {
	//dbg(@"appdelegate - loading item at index: %d from set %@", index, items);
	[[browseController webView] loadItemAtIndex: index fromSet:items];
	[self showViewer:self];
}

- (void)showNavigation: (id) sender {
	dbg(@"Navigation!");
	[self refreshItemLists];
	[[browseController webView] showCurrentItemInItemList: [mainController itemList]];
	[browseController deactivate];
	[self setViewToShowItem: NO];
	[mainController activate];
}

- (void) removeBrowseView {
	[[browseController view] removeFromSuperview];
}

- (void) setViewToShowItem:(BOOL) showItemView {
	BOOL withAnimation = !loading;
	inItemViewMode = showItemView;
	
	// tab / navigation bar:
	[[mainController tabBar] setHidden: showItemView];
	[[[mainController selectedViewController] navigationBar] setHidden: showItemView];
	
	// viewer
	if(showItemView) {
		[[mainController view] addSubview:[browseController view]];
		CGRect frame = [[mainController view] bounds];
		frame.origin = CGPointMake(0,0);
		[[browseController view] setFrame: frame];
		[[browseController view] setHidden:NO];
	} else {
		[self removeBrowseView];
	}
	[[mainController view] layoutSubviews];
}

- (void)showViewer: (id) sender {
	dbg(@"Viewer!");
	[mainController deactivate];
	[self setViewToShowItem: YES];
	[browseController activate];
}

- (void) refreshItemLists {
	for(id controller in [[mainController navController] viewControllers]) {
		[controller refresh:self];
	}
}

- (IBAction) toggleOptions: (id) sender {
	UIView * currentView = [[[mainController navController] topViewController] view];
	id subviews = [currentView subviews];
	if([subviews containsObject: optionsView]) {
		dbg(@"hiding options");
		[optionsView removeFromSuperview];
		[self refreshItemLists];
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
	NSString * tag = [appSettings getLastViewedTag];
	dbg(@"last viewed item = %@", itemID);
	dbg(@"last viewed tag = %@", tag);
	[self showNavigation: self];
	if(!(itemID == nil || [itemID length] == 0 || tag == nil || [tag length] == 0)) {
		dbg(@"loading tag %@, item %@", tag, itemID);
		[itemListDelegate loadItemWithID:itemID fromTag: tag];
	}
	[window addSubview:[mainController view]];
	loading = NO;
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

