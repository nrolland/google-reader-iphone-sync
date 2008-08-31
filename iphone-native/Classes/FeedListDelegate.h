#import <UIKit/UIKit.h>
#import <Foundation/Foundation.h>

@interface FeedListDelegate : UITableViewController {
	IBOutlet id appSettings;
	NSArray * feedList;
	NSArray * selectedFeedList;
	IBOutlet id cell;
}

@end
