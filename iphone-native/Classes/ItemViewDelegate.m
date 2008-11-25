#import "ItemViewDelegate.h"
#import "TCHelpers.h"


@implementation ItemViewDelegate

- (BOOL) webView:(id) view shouldStartLoadWithRequest:(NSURLRequest *) request navigationType:(UIWebViewNavigationType) type
{
	if(type == UIWebViewNavigationTypeLinkClicked) {
		if([[self globalAppSettings] openLinksInSafari]) {
			dbg(@"opening url in safari: %@", [request URL]);
			[[self globalApp] openURL: [request URL]];
			return NO;
		}
	}
	return YES;
}

- (void) showSpinner:(BOOL) doShow {
	[spinner setHidden: !doShow];
	doShow ? [spinner startAnimating] : [spinner stopAnimating];
}

- (void) webViewDidStartLoad:(id) sender {
	[self showSpinner: YES];
}

- (void) webViewDidFinishLoad:(id) sender {
	[self showSpinner:NO];
}

@end
