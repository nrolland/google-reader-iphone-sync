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
	[webView load];
}

- (void) deactivate {
	[webView deactivate];
}

@end
