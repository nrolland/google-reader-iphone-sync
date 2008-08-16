#import "StripedView.h"

@implementation StripedView

-(void) awakeFromNib {
	[self setBackgroundColor: [UIColor groupTableViewBackgroundColor]];
}

- (void)dealloc {
	[super dealloc];
}


@end
