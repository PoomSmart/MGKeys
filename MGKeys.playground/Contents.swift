import UIKit
import CommonCrypto

func CalculateObfuscatedKey(key: String) -> String
{
    let pre = ("MGCopyAnswer" + key as String)
    var hash = [UInt8](repeating: 0, count:Int(CC_MD5_DIGEST_LENGTH))
        CC_MD5(pre, UInt32(pre.count), &hash)
    let md5Data = NSData(bytes: hash, length: Int(CC_MD5_DIGEST_LENGTH))
    let obfuscatedKey = md5Data.base64EncodedString()
    return obfuscatedKey.substring(to: String.Index(encodedOffset: 22))
}

// 0D3qCmmfJ/i1mpmjOsV7EA - confirmed
CalculateObfuscatedKey(key: "ScreenSerialNumber")

// 0AJUv/uYPsRiZNGpWJ7zfg - guessed
CalculateObfuscatedKey(key: "DeviceSupportsSpokenMessages")

// M+WPVivF4iTnm1CC8c6h+A (haptic) - guessed
CalculateObfuscatedKey(key: "pre-warm-disabled")
