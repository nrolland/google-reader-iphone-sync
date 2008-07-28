//
//  GoogleFeed.m
//  Feeds2
//
//  Created by Tim Cuthbertson on 26/07/08.
//  Copyright 2008 __MyCompanyName__. All rights reserved.
//

#import "GoogleFeed.h"


@implementation GoogleFeed
-(BOOL) authWithUser: nusername password:npassword {
	username = nusername;
	pass = npassword;
	[self auth];
}

-(BOOL) auth {
}	

-(void) addNewItems {
}

@end
