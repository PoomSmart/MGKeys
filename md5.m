#import <Foundation/Foundation.h>

NSString *md5StringForObfuscatedKey(NSString *inObfuscatedKey) {
    if ([inObfuscatedKey length] <= 0) return nil;

    NSString *base64String = [NSString stringWithFormat:@"%@==", inObfuscatedKey];

    NSData *md5Data = [[NSData alloc] initWithBase64EncodedString:base64String options:0];
    if ([md5Data length] < 16) return nil;

    const uint8_t *md5Bytes = [md5Data bytes];
    NSString *md5String = [NSString stringWithFormat:@"%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x", md5Bytes[0], md5Bytes[1], md5Bytes[2], md5Bytes[3], md5Bytes[4], md5Bytes[5], md5Bytes[6], md5Bytes[7], md5Bytes[8], md5Bytes[9], md5Bytes[10], md5Bytes[11], md5Bytes[12], md5Bytes[13], md5Bytes[14], md5Bytes[15]];
    
    return md5String;
}

int main(int argc, const char * argv[]) {
    @autoreleasepool {
        if (argc < 2) {
            printf("Please enter a string to obfuscate\n");
            return 1;
        }

        NSString *inputString = [NSString stringWithUTF8String:argv[1]];
        NSString *outputString = md5StringForObfuscatedKey(inputString);
        if (outputString != nil) {
            printf("%s\n", [outputString UTF8String]);
        } else {
            printf("Invalid input for obfuscation\n");
            return 1;
        }
    }
    return 0;
}
