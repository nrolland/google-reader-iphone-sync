#import <UIKit/UIKit.h>
#import <Foundation/Foundation.h>
#import "ItemDB.h"

@interface ItemSet : NSObject {
	NSString * tag;
	NSArray * itemSet;
	id db;
	BOOL includeReadItems;
}

- (id) items;
@end
