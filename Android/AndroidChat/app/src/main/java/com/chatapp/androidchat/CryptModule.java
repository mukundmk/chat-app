package com.chatapp.androidchat;

import android.util.Base64;
import android.util.Log;

import org.apache.commons.ssl.OpenSSL;

import java.security.KeyFactory;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.security.SecureRandom;
import java.security.spec.RSAPrivateKeySpec;
import java.security.spec.X509EncodedKeySpec;
import org.bouncycastle.asn1.ASN1Sequence;
import org.bouncycastle.asn1.pkcs.RSAPrivateKeyStructure;

import javax.crypto.Cipher;

/**
 * Created by mrp(What a Scam!)on 29/4/15.
 */
public class CryptModule {
    private final PrivateKey privateKey;
    private final PublicKey publicKey;
    private final PublicKey myPublicKey;
    static final String AB = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
    static SecureRandom rnd = new SecureRandom();

    public CryptModule(String privateKey, String publicKey)throws Exception{
        KeyFactory kf = KeyFactory.getInstance("RSA");
        publicKey = publicKey.replace("-----BEGIN PUBLIC KEY-----\n","").replace("-----END PUBLIC KEY-----","");
        this.publicKey = kf.generatePublic(new X509EncodedKeySpec(Base64.decode(publicKey, 0)));
        privateKey = privateKey.replace("-----BEGIN RSA PRIVATE KEY-----\n","").replace("-----END RSA PRIVATE KEY-----","");
        byte [] asn1PrivateKeyBytes = Base64.decode(privateKey,0);
        RSAPrivateKeyStructure asn1PrivKey = new RSAPrivateKeyStructure((ASN1Sequence) ASN1Sequence.fromByteArray(asn1PrivateKeyBytes));
        this.privateKey = kf.generatePrivate(new RSAPrivateKeySpec(asn1PrivKey.getModulus(), asn1PrivKey.getPrivateExponent()));
        this.myPublicKey = this.publicKey;
    }
    public CryptModule(String privateKey, String publicKey, String myPublicKey)throws Exception{
        KeyFactory kf = KeyFactory.getInstance("RSA");
        publicKey = publicKey.replace("-----BEGIN PUBLIC KEY-----\n","").replace("-----END PUBLIC KEY-----","");
        this.publicKey = kf.generatePublic(new X509EncodedKeySpec(Base64.decode(publicKey, 0)));
        myPublicKey = myPublicKey.replace("-----BEGIN PUBLIC KEY-----\n","").replace("-----END PUBLIC KEY-----","");
        this.myPublicKey = kf.generatePublic(new X509EncodedKeySpec(Base64.decode(myPublicKey, 0)));
        privateKey = privateKey.replace("-----BEGIN RSA PRIVATE KEY-----\n","").replace("-----END RSA PRIVATE KEY-----","");
        byte [] asn1PrivateKeyBytes = Base64.decode(privateKey,0);
        RSAPrivateKeyStructure asn1PrivKey = new RSAPrivateKeyStructure((ASN1Sequence) ASN1Sequence.fromByteArray(asn1PrivateKeyBytes));
        this.privateKey = kf.generatePrivate(new RSAPrivateKeySpec(asn1PrivKey.getModulus(), asn1PrivKey.getPrivateExponent()));
    }
    public String[] encrypt(String plaintext)throws Exception{
        String[] encrypted_message = new String[3];
        char[] pass = randomString(18).toCharArray();
        byte[] encodePass = Base64.encode(new String(pass).getBytes(),Base64.DEFAULT);
        byte[] data = plaintext.getBytes();
        byte[] encrypted = OpenSSL.encrypt("aes-256-cbc", pass ,data);
        Cipher c = Cipher.getInstance("RSA/ECB/PKCS1PADDING","BC");
        c.init(Cipher.ENCRYPT_MODE, this.publicKey);
        byte[] encrypted_key = Base64.encode(c.doFinal(encodePass),Base64.DEFAULT);

        c = Cipher.getInstance("RSA/ECB/PKCS1PADDING","BC");
        c.init(Cipher.ENCRYPT_MODE, this.myPublicKey);
        byte[] encrypted_key_2 = Base64.encode(c.doFinal(encodePass),Base64.DEFAULT);
        Log.d("key",new String(Base64.decode(encrypted_key_2,Base64.DEFAULT)));
        Log.d("pass",new String(pass));
        Log.d("key",new String(Base64.encode(new String(pass).getBytes(),Base64.DEFAULT)));
        encrypted_message[0]= new String(encrypted);
        encrypted_message[1]= new String(encrypted_key);
        encrypted_message[2]= new String(encrypted_key_2);
        return encrypted_message;
    }
    public String decrypt(String ciphertext, String encrypted_key)throws Exception{
        Cipher c = Cipher.getInstance("RSA/ECB/PKCS1PADDING","BC");
        c.init(Cipher.DECRYPT_MODE, this.privateKey);
        byte[] aes_key = Base64.decode(c.doFinal(Base64.decode(encrypted_key,Base64.DEFAULT)),Base64.DEFAULT);
        char[] pass = new String(aes_key).toCharArray();
        byte[] data = ciphertext.getBytes();
        byte[] decrypted = OpenSSL.decrypt("aes-256-cbc", pass, data);
        String plaintext = new String(decrypted);
        return plaintext;
    }
    private String randomString( int len )
    {
        StringBuilder sb = new StringBuilder( len );
        for( int i = 0; i < len; i++ )
            sb.append( AB.charAt( rnd.nextInt(AB.length()) ) );
        return sb.toString();
    }
}
