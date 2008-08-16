#import "tcHelpers.h"
#import "TCViewExtensions.h"

@implementation UIView (TCViewExtensions)

- (void) startAnimating {
	[UIView beginAnimations:nil context: nil];
}

- (void) endAnimating{
	[UIView commitAnimations];
}

- (void) animateSlideInToRect:(CGRect) targetRect fromDirection:(NSString *) direction {
	float targetHeight = targetRect.size.height - targetRect.origin.y;
	float targetWidth = targetRect.size.width - targetRect.origin.x;
	dbg(@"targetWidth = %0.1f", targetWidth);
	dbg(@"targetHeight = %0.1f", targetHeight);
	CGPoint targetCenter = CGPointMake(targetRect.origin.x + (targetWidth / 2) , targetRect.origin.y + (targetHeight / 2));
	CGPoint initialCenter = targetCenter;

	if(direction == nil || [direction isEqualToString: @"left"]) {
		initialCenter.x -= targetWidth;
	} else if([direction isEqualToString: @"right"]) {
		initialCenter.x += targetWidth;
	} else if([direction isEqualToString: @"top"]) {
		initialCenter.y += targetHeight;
	} else if([direction isEqualToString: @"bottom"]) {
		initialCenter.y -= targetHeight;
	}
	[self animateSlideFromCenter: initialCenter toCenter: targetCenter];
}

- (void) animateSlideFromCenter:(CGPoint) fromPoint toCenter:(CGPoint) toPoint{
	dbg(@"animating item %@ from (%0.1f,%0.1f) to (%0.1f,%0.1f)", self, fromPoint.x, fromPoint.y, toPoint.x, toPoint.y);
	[self setAlpha:0.0];
	[self setCenter: fromPoint];
	[self startAnimating];
	[self setCenter: toPoint];
	[self setAlpha:1.0];
	[self endAnimating];
}


- (void) animateFadeIn {
	[self setAlpha: 0.0];
	[self startAnimating];
	[self setAlpha: 1.0];
	[self endAnimating];
}

- (void) animateFadeOutThenTell:(id) callbackObject withSelector:(SEL) completionSelector {
	[self setAlpha: 1.0];
	[self startAnimating];
	[UIView setAnimationDelegate: callbackObject];
	[UIView setAnimationDidStopSelector: completionSelector];
	[self setAlpha: 0.0];
	[self endAnimating];
}

@end
