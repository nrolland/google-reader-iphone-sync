#import <UIKit/UIKit.h>
#import <Foundation/Foundation.h>
#import "tcItemDB.h"

@interface ItemListDelegate : UITableViewController {
	IBOutlet tcItemDB * db;
	id itemSet;
	UIImage * starredImage;
	UIImage * readImage;
	UIImage * readAndStarredImage;
}

- (id) itemSet;
@end
