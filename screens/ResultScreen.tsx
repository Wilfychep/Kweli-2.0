import React, { useEffect, useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    TouchableOpacity,
    Linking,
    ActivityIndicator,
    ScrollView,
    Share
} from 'react-native';
import { useLocalSearchParams, router } from 'expo-router';
import { Feather, MaterialIcons } from '@expo/vector-icons';
import * as Clipboard from 'expo-clipboard';

type ResultParams = {
    result?: 'real' | 'fake';
    image_hash?: string;
    tx_hash?: string;
    filename?: string;
    confidence?: string;
};

const ResultScreen: React.FC = () => {
    const {
        result = 'fake',
        image_hash,
        tx_hash,
        filename,
        confidence
    } = useLocalSearchParams<ResultParams>();

    const [isCopying, setIsCopying] = useState(false);
    const [txStatus, setTxStatus] = useState<'pending' | 'confirmed' | 'failed'>('pending');

    useEffect(() => {
        if (tx_hash) {
            // Simulate transaction confirmation (replace with actual check)
            const timer = setTimeout(() => {
                setTxStatus('confirmed');
            }, 5000);

            return () => clearTimeout(timer);
        }
    }, [tx_hash]);

    const handleOpenExplorer = () => {
        if (!tx_hash) return;
        const explorerUrl = `https://sepolia.starkscan.co/tx/${tx_hash}`;
        Linking.openURL(explorerUrl);
    };

    const copyToClipboard = async (text: string) => {
        setIsCopying(true);
        await Clipboard.setStringAsync(text);
        setTimeout(() => setIsCopying(false), 1500);
    };

    const shareResult = async () => {
        try {
            await Share.share({
                message: `This media was analyzed as ${result} (Confidence: ${confidence}%). Transaction: https://sepolia.starkscan.co/tx/${tx_hash}`,
                title: 'Deepfake Analysis Result'
            });
        } catch (error) {
            console.error('Sharing failed:', error);
        }
    };

    const isAuthentic = result === 'real';
    const confidencePercentage = confidence ? Math.round(Number(confidence) * 100) : 0;

    return (
        <ScrollView contentContainerStyle={styles.container}>
            {/* Header */}
            <View style={styles.header}>
                <TouchableOpacity onPress={() => router.back()}>
                    <Feather name="arrow-left" size={24} color="#007AFF" />
                </TouchableOpacity>
                <Text style={styles.headerTitle}>Analysis Result</Text>
                <View style={{ width: 24 }} /> {/* Spacer */}
            </View>

            {/* Main Result Card */}
            <View style={[styles.resultCard, isAuthentic ? styles.authenticCard : styles.fakeCard]}>
                <MaterialIcons
                    name={isAuthentic ? 'verified' : 'warning'}
                    size={48}
                    color={isAuthentic ? '#4CAF50' : '#F44336'}
                />
                <Text style={styles.resultText}>
                    {isAuthentic ? 'Authentic Content' : 'Potential Deepfake'}
                </Text>
                {confidence && (
                    <View style={styles.confidenceBadge}>
                        <Text style={styles.confidenceText}>
                            {confidencePercentage}% Confidence
                        </Text>
                    </View>
                )}
            </View>

            {/* File Information */}
            <View style={styles.infoSection}>
                <Text style={styles.sectionTitle}>Media Information</Text>
                {filename && (
                    <View style={styles.infoRow}>
                        <Feather name="file" size={20} color="#666" />
                        <Text style={styles.infoText} numberOfLines={1} ellipsizeMode="middle">
                            {filename}
                        </Text>
                    </View>
                )}
            </View>

            {/* Blockchain Verification */}
            <View style={styles.infoSection}>
                <Text style={styles.sectionTitle}>Blockchain Verification</Text>

                {image_hash && (
                    <View style={styles.infoRow}>
                        <Feather name="hash" size={20} color="#666" />
                        <View style={styles.hashContainer}>
                            <Text style={styles.infoText} numberOfLines={1} ellipsizeMode="middle">
                                {image_hash}
                            </Text>
                            <TouchableOpacity
                                onPress={() => copyToClipboard(image_hash)}
                                style={styles.copyButton}
                            >
                                {isCopying ? (
                                    <Text style={styles.copiedText}>Copied!</Text>
                                ) : (
                                    <Feather name="copy" size={16} color="#007AFF" />
                                )}
                            </TouchableOpacity>
                        </View>
                    </View>
                )}

                {tx_hash && (
                    <>
                        <View style={styles.infoRow}>
                            <Feather name="link" size={20} color="#666" />
                            <View style={styles.hashContainer}>
                                <Text style={styles.infoText} numberOfLines={1} ellipsizeMode="middle">
                                    {tx_hash}
                                </Text>
                                <TouchableOpacity
                                    onPress={() => copyToClipboard(tx_hash)}
                                    style={styles.copyButton}
                                >
                                    <Feather name="copy" size={16} color="#007AFF" />
                                </TouchableOpacity>
                            </View>
                        </View>

                        <View style={styles.statusRow}>
                            <View style={[styles.statusIndicator,
                            txStatus === 'confirmed' ? styles.confirmed :
                                txStatus === 'failed' ? styles.failed : styles.pending
                            ]} />
                            <Text style={styles.statusText}>
                                {txStatus === 'confirmed' ? 'Confirmed on Starknet' :
                                    txStatus === 'failed' ? 'Transaction failed' : 'Confirming...'}
                            </Text>
                            {txStatus === 'pending' && (
                                <ActivityIndicator size="small" color="#FFA000" style={styles.loading} />
                            )}
                        </View>

                        <TouchableOpacity
                            style={styles.explorerButton}
                            onPress={handleOpenExplorer}
                        >
                            <Feather name="external-link" size={18} color="white" />
                            <Text style={styles.explorerButtonText}>View on StarkScan</Text>
                        </TouchableOpacity>
                    </>
                )}
            </View>

            {/* Action Buttons */}
            <View style={styles.buttonGroup}>
                <TouchableOpacity
                    style={[styles.actionButton, styles.shareButton]}
                    onPress={shareResult}
                >
                    <Feather name="share-2" size={20} color="white" />
                    <Text style={styles.actionButtonText}>Share Result</Text>
                </TouchableOpacity>

                <TouchableOpacity
                    style={[styles.actionButton, styles.newAnalysisButton]}
                    onPress={() => router.replace('/upload')}
                >
                    <Feather name="plus" size={20} color="white" />
                    <Text style={styles.actionButtonText}>New Analysis</Text>
                </TouchableOpacity>
            </View>
        </ScrollView>
    );
};

const styles = StyleSheet.create({
    container: {
        flexGrow: 1,
        backgroundColor: '#f9f9f9',
        padding: 20,
        paddingBottom: 40,
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 24,
    },
    headerTitle: {
        fontSize: 20,
        fontWeight: '600',
        color: '#333',
    },
    resultCard: {
        backgroundColor: 'white',
        borderRadius: 12,
        padding: 24,
        alignItems: 'center',
        marginBottom: 24,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 6,
        elevation: 3,
    },
    authenticCard: {
        borderLeftWidth: 4,
        borderLeftColor: '#4CAF50',
    },
    fakeCard: {
        borderLeftWidth: 4,
        borderLeftColor: '#F44336',
    },
    resultText: {
        fontSize: 22,
        fontWeight: 'bold',
        marginTop: 12,
        marginBottom: 8,
    },
    confidenceBadge: {
        backgroundColor: '#E8F5E9',
        paddingHorizontal: 12,
        paddingVertical: 6,
        borderRadius: 20,
        marginTop: 8,
    },
    confidenceText: {
        color: '#2E7D32',
        fontWeight: '500',
    },
    infoSection: {
        backgroundColor: 'white',
        borderRadius: 12,
        padding: 16,
        marginBottom: 16,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.05,
        shadowRadius: 3,
        elevation: 2,
    },
    sectionTitle: {
        fontSize: 16,
        fontWeight: '600',
        color: '#444',
        marginBottom: 12,
    },
    infoRow: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 12,
    },
    infoText: {
        marginLeft: 12,
        color: '#555',
        flex: 1,
    },
    hashContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        flex: 1,
        marginLeft: 12,
        backgroundColor: '#f5f5f5',
        padding: 10,
        borderRadius: 8,
    },
    copyButton: {
        marginLeft: 8,
        padding: 4,
    },
    copiedText: {
        color: '#007AFF',
        fontSize: 12,
    },
    statusRow: {
        flexDirection: 'row',
        alignItems: 'center',
        marginTop: 8,
        marginBottom: 16,
    },
    statusIndicator: {
        width: 10,
        height: 10,
        borderRadius: 5,
        marginRight: 8,
    },
    pending: {
        backgroundColor: '#FFA000',
    },
    confirmed: {
        backgroundColor: '#4CAF50',
    },
    failed: {
        backgroundColor: '#F44336',
    },
    statusText: {
        color: '#666',
        fontSize: 14,
    },
    loading: {
        marginLeft: 8,
    },
    explorerButton: {
        flexDirection: 'row',
        backgroundColor: '#007AFF',
        padding: 14,
        borderRadius: 8,
        alignItems: 'center',
        justifyContent: 'center',
        marginTop: 8,
    },
    explorerButtonText: {
        color: 'white',
        fontWeight: '500',
        marginLeft: 8,
    },
    buttonGroup: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginTop: 24,
    },
    actionButton: {
        flexDirection: 'row',
        padding: 14,
        borderRadius: 8,
        alignItems: 'center',
        justifyContent: 'center',
        flex: 1,
        marginHorizontal: 6,
    },
    shareButton: {
        backgroundColor: '#757575',
    },
    newAnalysisButton: {
        backgroundColor: '#007AFF',
    },
    actionButtonText: {
        color: 'white',
        fontWeight: '500',
        marginLeft: 8,
    },
});

export default ResultScreen;
