#import "Feeds2AppDelegate.h"
#import "tcWebView.h"
#import "tcHelpers.h"

@implementation Feeds2AppDelegate

@synthesize window;

- (void)applicationDidFinishLaunching:(UIApplication *)application {
	// Add the tab bar controller's current view as a subview of the window
	dbg(@"Loaded...");

	// ensure the app's docs directory exists
	NSString *docsPath = [NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES) objectAtIndex:0];
	appDocsPath = [docsPath stringByAppendingPathComponent: @"GRiS"];
	dbg(@"apps doc path: %@", appDocsPath);
	if(![tcHelpers ensureDirectoryExists: appDocsPath]){
		[tcHelpers alertCalled: @"DB Error" saying: [NSString stringWithFormat: @"Could not create app directory at:\n%@", appDocsPath]];
		[[UIApplication sharedApplication] terminate];
	}
	
	// set up the well-known path that the python app will use
	NSFileManager *fileManager = [NSFileManager defaultManager];
	NSError *symlink_error;
	NSString * varPath = @"/var/mobile/.GRiS";
	[fileManager removeItemAtPath: varPath error:nil];
	if(![fileManager createSymbolicLinkAtPath: varPath withDestinationPath:appDocsPath error:&symlink_error]){
		[tcHelpers alertCalled: @"Symlink Error" saying: [NSString stringWithFormat: @"Could not symlink to: %@", appDocsPath]];
		NSLog(@"Error %@ while linking: %@::%@",
			[symlink_error code],
			[symlink_error domain],
			[symlink_error localizedDescription]);
		[[UIApplication sharedApplication] terminate];
	} else {
		dbg(@"symlink created from @% -> %@", varPath, appDocsPath);
	}
	
	// now some actual UI: setup the viewer
	[self showViewer: self];
}

- (NSString *) appDocsPath { return appDocsPath; }

- (void)showNavigation: (id) sender {
	[browseController deactivate];
	dbg(@"Navigation!");
}

- (void)showViewer: (id) sender {
	dbg(@"Viewer!");
	[browseController activate];
}

- (void)dealloc {
	[window release];
	[browseController release];
	[super dealloc];
}

@end

