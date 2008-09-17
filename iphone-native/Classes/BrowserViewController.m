#import "BrowserViewController.h"
#import "TCHelpers.h"

@implementation BrowserViewController
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
