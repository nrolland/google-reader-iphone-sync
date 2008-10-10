#import "StripedView.h"

@implementation StripedView

-(void) awakeFromNib {
	[self setBackgroundColor: [UIColor groupTableViewBackgroundColor]];
	[super awakeFromNib];
}

@end
