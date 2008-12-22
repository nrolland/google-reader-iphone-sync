#import "TCHelpers.h"
#import "TCViewExtensions.h"

@implementation UIView (TCViewExtensions)

- (void) fitToSuperview {
	[self fitTo: [self superview]];
}

- (void) fitTo:(UIView *) view {
	CGRect frame = [view bounds];
	frame.origin = CGPointMake(0,0);
	[self setFrame: frame];
}

- (void) fitToSuperviewWidth {
	CGRect frame = [[self superview] bounds];
	CGRect myFrame = [self bounds];
	myFrame.origin.x = 0;
	myFrame.size.width = frame.size.width;
	[self setFrame: myFrame];
}
	

- (void) startAnimating {
	[UIView beginAnimations:nil context: nil];
}

- (void) endAnimating{
	[UIView commitAnimations];
}

- (void) animateSlideInToRect:(CGRect) targetRect fromDirection:(NSString *) direction {
	float targetHeight = targetRect.size.height - targetRect.origin.y;
	float targetWidth = targetRect.size.width - targetRect.origin.x;
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

- (void) animateFade:(BOOL) fadingOut {
	if(fadingOut) {
		[self animateFadeOutThenTell:nil withSelector:nil];
	} else {
		[self animateFadeIn];
	}
}

- (void) animateFadeOutThenTell:(id) callbackObject withSelector:(SEL) completionSelector {
	[self setAlpha: 1.0];
	[self startAnimating];
	if(callbackObject){
		[UIView setAnimationDelegate: callbackObject];
		[UIView setAnimationDidStopSelector: completionSelector];
	}
	[self setAlpha: 0.0];
	[self endAnimating];
}

@end
