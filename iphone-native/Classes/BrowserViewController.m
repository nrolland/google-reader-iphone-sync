#import "BrowserViewController.h"
#import "TCHelpers.h"

@implementation BrowserViewController
- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
	if(interfaceOrientation == UIInterfaceOrientationPortraitUpsideDown) return NO;
	return YES;
}

- (id) webView { return webView; }

- (id) currentItemID {
	return [webView currentItemID];
}

- (void) activate {
	// id mainController = [[[UIApplication sharedApplication] delegate] mainController];
	// [[mainController view] addSubview:[self view]];
	// [[mainController tabBar] setHidden: YES];
//	[topLevelWindow addSubview:[self view]];
	// TODO: stop being underneath the statusbar. it does this for us when the screen rotates, so we must be able to do it somehow...
	// this is a hacky version that only works if it's in portrait mode:
//	[[self view] setCenter: CGPointMake(160,250)];
	[webView load];
}

- (void) deactivate {
//	[[self view] removeFromSuperview];
	[webView deactivate];
}

@end
