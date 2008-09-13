#import <UIKit/UIKit.h>
#import <Foundation/Foundation.h>
#import "ItemDB.h"

@interface ItemListDelegate : UITableViewController {
	IBOutlet ItemDB * db;
	id itemSet;
	UIImage * starredImage;
	UIImage * readImage;
	UIImage * readAndStarredImage;
	UIFont * cellFont;
	IBOutlet id settings;
	IBOutlet UITableView * listView;
	NSString * tag;
	NSString * feed;
}

- (id) itemSet;
@end
