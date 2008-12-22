#import <UIKit/UIKit.h>
#import <Foundation/Foundation.h>
#import "ItemDB.h"

@interface ItemListDelegate : NSObject {
	IBOutlet ItemDB * db;
	IBOutlet id optionsButton;
	id itemSet;
	UIImage * folderImage;
	UIImage * starredImage;
	UIImage * sharedImage;
	UIImage * sharedAndStarredImage;
	UIFont * cellFont;
	IBOutlet id settings;
	IBOutlet id navigationController;
	NSString * tag;
}

- (id) itemSet;
@end
