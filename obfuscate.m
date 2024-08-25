#import <CommonCrypto/CommonDigest.h>
#import <Foundation/Foundation.h>
#import "mapping.h"

NSString *obfuscate(const char *inString) {
    char buffer[256] = { 0 };
    snprintf(buffer, sizeof(buffer), "%s%s", "MGCopyAnswer", inString);

    unsigned char md5Hash[CC_MD5_DIGEST_LENGTH] = { 0 };
    CC_MD5(buffer, (CC_LONG)strlen(buffer), md5Hash);

    NSData *md5Data = [NSData dataWithBytes:md5Hash length:CC_MD5_DIGEST_LENGTH];
    NSString *obfuscatedKey = [md5Data base64EncodedStringWithOptions:0];

    return [obfuscatedKey substringToIndex:22];
}

NSString *md5(NSString *inObfuscatedKey) {
    if ([inObfuscatedKey length] <= 0) return nil;

    NSString *base64String = [NSString stringWithFormat:@"%@==", inObfuscatedKey];

    NSData *md5Data = [[NSData alloc] initWithBase64EncodedString:base64String options:0];
    if ([md5Data length] < 16) return nil;

    const uint8_t *md5Bytes = [md5Data bytes];
    NSString *md5String = [NSString stringWithFormat:@"%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x", md5Bytes[0], md5Bytes[1], md5Bytes[2], md5Bytes[3], md5Bytes[4], md5Bytes[5], md5Bytes[6], md5Bytes[7], md5Bytes[8], md5Bytes[9], md5Bytes[10], md5Bytes[11], md5Bytes[12], md5Bytes[13], md5Bytes[14], md5Bytes[15]];
    
    return md5String;
}

NSString *mapDeobfuscated(NSString *inString) {
    const char *inStringChars = [inString UTF8String];
    for (int i = 0; i < sizeof(keyMappingTable) / sizeof(keyMappingTable[0]); i++) {
        const char *obfuscatedKey = keyMappingTable[i].obfuscatedKey;
        if (strcmp(inStringChars, obfuscatedKey) == 0) {
            const char *deobfuscatedKey = keyMappingTable[i].key;
            if (deobfuscatedKey == NULL) return @"NULL";
            return [NSString stringWithUTF8String:deobfuscatedKey];
        }
    }
    return @"CANNOT FIND KEY";
}

int main(int argc, const char * argv[]) {
    @autoreleasepool {
        if (argc < 3) {
            printf("Usage: %s <mode> <key>\n", argv[0]);
            return 1;
        }

        NSString *mode = [NSString stringWithUTF8String:argv[1]];
        NSString *key = [NSString stringWithUTF8String:argv[2]];

        if ([mode isEqualToString:@"obfuscate"]) {
            printf("%s\n", [obfuscate([key UTF8String]) UTF8String]);
        } else if ([mode isEqualToString:@"md5"]) {
            printf("%s\n", [md5(key) UTF8String]);
        } else if ([mode isEqualToString:@"map-deobfuscated"]) {
            printf("%s\n", [mapDeobfuscated(key) UTF8String]);
        } else {
            printf("Unknown mode: %s\n", [mode UTF8String]);
            return 1;
        }
    }
    return 0;
}
