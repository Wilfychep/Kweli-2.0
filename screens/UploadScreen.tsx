import React, { useState } from 'react';
import {
    View,
    Text,
    Button,
    Image,
    StyleSheet,
    ActivityIndicator,
    Alert,
    Platform,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { Video, ResizeMode } from 'expo-av';
import { useRouter } from 'expo-router';

// Configuration
const API_BASE_URL = Platform.select({
    web: 'http://localhost:5000',
    default: 'http://192.168.180.147:5000'
});

const UploadScreen: React.FC = () => {
    const [fileUri, setFileUri] = useState<string | null>(null);
    const [fileType, setFileType] = useState<'image' | 'video' | null>(null);
    const [file, setFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const router = useRouter();

    const pickMedia = async () => {
        if (Platform.OS === 'web') {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = 'image/*';
            input.onchange = () => {
                const selectedFile = input.files?.[0];
                if (selectedFile) {
                    setFileUri(URL.createObjectURL(selectedFile));
                    setFileType('image');
                    setFile(selectedFile);
                }
            };
            input.click();
        } else {
            const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
            if (!permission.granted) {
                Alert.alert('Permission required', 'Please grant media library permissions.');
                return;
            }

            const result = await ImagePicker.launchImageLibraryAsync({
                mediaTypes: ImagePicker.MediaTypeOptions.Images,
                allowsEditing: false,
                quality: 1,
            });

            if (!result.canceled && result.assets?.[0]) {
                const asset = result.assets[0];
                setFileUri(asset.uri);
                setFileType('image');
                setFile(null);
            }
        }
    };

    const uploadMedia = async () => {
        if (!fileUri || !fileType) {
            Alert.alert('Error', 'No file selected');
            return;
        }

        setUploading(true);
        const formData = new FormData();

        try {
            // Prepare the file for upload
            if (Platform.OS === 'web' && file) {
                formData.append('file', file);
            } else if (fileUri) {
                formData.append('file', {
                    uri: fileUri,
                    name: 'image.jpg',
                    type: 'image/jpeg',
                } as any);
            }

            // Send to backend
            const response = await fetch(`${API_BASE_URL}/upload`, {
                method: 'POST',
                body: formData,
                headers: {
                    'Accept': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('Backend response:', data);

            if (data.status === 'success') {
                router.push({
                    pathname: '/result',
                    params: {
                        result: data.prediction, // 'real' or 'fake'
                        image_hash: data.image_hash,
                        tx_hash: data.tx_hash,
                        filename: data.filename
                    },
                });
            } else {
                Alert.alert('Upload Failed', data.message || 'Unknown error occurred');
            }
        } catch (error) {
            console.error('Upload error:', error);
            Alert.alert('Error', 'Failed to upload and analyze image. Please try again.');
        } finally {
            setUploading(false);
        }
    };

    return (
        <View style={styles.container}>
            <Text style={styles.title}>Upload Image for Analysis</Text>

            <Button
                title="Select Image"
                onPress={pickMedia}
                disabled={uploading}
            />

            {fileUri && fileType === 'image' && (
                <Image
                    source={{ uri: fileUri }}
                    style={styles.preview}
                    resizeMode="contain"
                />
            )}

            {uploading ? (
                <View style={styles.uploadingContainer}>
                    <ActivityIndicator size="large" color="#0000ff" />
                    <Text style={styles.uploadingText}>Analyzing image...</Text>
                </View>
            ) : (
                fileUri && (
                    <Button
                        title="Upload & Analyze"
                        onPress={uploadMedia}
                        color="#007AFF"
                    />
                )
            )}
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 20,
        backgroundColor: '#fff',
    },
    title: {
        fontSize: 22,
        fontWeight: 'bold',
        marginBottom: 30,
        textAlign: 'center',
    },
    preview: {
        width: '100%',
        height: 300,
        marginVertical: 20,
        borderRadius: 8,
    },
    uploadingContainer: {
        marginTop: 20,
        alignItems: 'center',
    },
    uploadingText: {
        marginTop: 10,
        color: '#666',
    },
});

export default UploadScreen;