#import "Feeds2AppDelegate.h"
#import "tcWebView.h"
#import "tcHelpers.h"

@implementation Feeds2AppDelegate

@synthesize window;

- (void) applicationWillTerminate:(id) sender {
	dbg(@"teminating...");
	[db dealloc];
	[appSettings dealloc];
}

- (id) settings { return appSettings; }

- (void)applicationDidFinishLaunching:(UIApplication *)application {
	// Add the tab bar controller's current view as a subview of the window
	dbg(@"Loaded...");

	[window setBackgroundColor: [UIColor groupTableViewBackgroundColor]];
	//[self showViewer: self];
	[self showNavigation: self];
}

- (void) loadItemAtIndex: (int) index fromSet:(id) items {
	dbg(@"appdelegate - loading item at index: %d from set %@", index, items);
	[[browseController webView] loadItemAtIndex: index fromSet:items];
	[self showViewer:self];
}

- (void)showNavigation: (id) sender {
	dbg(@"Navigation!");
	[[browseController webView] showCurrentItemInItemList: [mainController itemList]];
	[browseController deactivate];
	[mainController activate];
}

- (void)showViewer: (id) sender {
	dbg(@"Viewer!");
	[mainController deactivate];
	[browseController activate];
}

- (void)dealloc {
	[window release];
	[browseController release];
	[super dealloc];
}

@end

