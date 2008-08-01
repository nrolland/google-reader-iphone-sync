#import <UIKit/UIKit.h>
#import <Foundation/Foundation.h>
#import "tcItemDB.h"

@interface ItemListDelegate : UITableViewController {
	IBOutlet tcItemDB * db;
	id itemSet;
}

- (id) itemSet;
@end
