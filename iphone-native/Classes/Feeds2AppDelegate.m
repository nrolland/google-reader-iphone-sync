#import "Feeds2AppDelegate.h"
#import "tcWebView.h"

@implementation Feeds2AppDelegate

@synthesize window;

- (void)applicationDidFinishLaunching:(UIApplication *)application {
	// Add the tab bar controller's current view as a subview of the window
	NSLog(@"Loaded...");
	[self showViewer: self];
}

- (void)showNavigation: (id) sender {
	[browseController deactivate];
	NSLog(@"Navigation!");
}

- (void)showViewer: (id) sender {
	NSLog(@"Viewer!");
	[browseController activate];
}

- (void)dealloc {
	[window release];
	[browseController release];
	[super dealloc];
}

@end

