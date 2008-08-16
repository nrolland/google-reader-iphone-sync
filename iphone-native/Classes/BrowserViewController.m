#import "BrowserViewController.h"

@implementation BrowserViewController
- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    return YES;
}

- (id) webView { return webView; }

- (void) activate {
	[topLevelWindow addSubview:[self view]];
	// TODO: stop being underneath the statusbar. it does this for us when the screen rotates, so we must be able to do it somehow...
	// this is a hacky version that only works if it's in portrait mode:
	[[self view] setCenter: CGPointMake(160,250)];
	NSLog(@"webview loading...");
	[webView load];
	NSLog(@"webview loaded...");
}

- (void) deactivate {
	[[self view] removeFromSuperview];
	[webView deactivate];
}

@end
