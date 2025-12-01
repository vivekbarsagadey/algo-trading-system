import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  ScrollView,
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import { brokerService } from '../services/broker';
import { BrokerStatus } from '../types';

interface BrokerSetupScreenProps {
  userId: string;
}

export default function BrokerSetupScreen({ userId }: BrokerSetupScreenProps) {
  const [brokers, setBrokers] = useState<string[]>([]);
  const [selectedBroker, setSelectedBroker] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [apiSecret, setApiSecret] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<BrokerStatus | null>(null);

  useEffect(() => {
    loadBrokers();
    loadStatus();
  }, []);

  const loadBrokers = async () => {
    try {
      const supportedBrokers = await brokerService.getSupportedBrokers();
      setBrokers(supportedBrokers);
      if (supportedBrokers.length > 0) {
        setSelectedBroker(supportedBrokers[0]);
      }
    } catch (error) {
      console.error('Failed to load brokers:', error);
    }
  };

  const loadStatus = async () => {
    try {
      const brokerStatus = await brokerService.getStatus(userId);
      setStatus(brokerStatus);
    } catch (error) {
      console.error('Failed to load broker status:', error);
    }
  };

  const handleConnect = async () => {
    if (!apiKey || !apiSecret) {
      Alert.alert('Error', 'Please enter API key and secret');
      return;
    }

    setLoading(true);
    try {
      await brokerService.connect({
        broker_name: selectedBroker,
        api_key: apiKey,
        api_secret: apiSecret,
        user_id: userId,
      });
      Alert.alert('Success', 'Broker connected successfully');
      loadStatus();
      setApiKey('');
      setApiSecret('');
    } catch (error: any) {
      Alert.alert(
        'Connection Failed',
        error.response?.data?.detail || 'Failed to connect to broker'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleDisconnect = async () => {
    setLoading(true);
    try {
      await brokerService.disconnect(userId);
      Alert.alert('Success', 'Broker disconnected');
      setStatus(null);
    } catch (error: any) {
      Alert.alert(
        'Disconnect Failed',
        error.response?.data?.detail || 'Failed to disconnect'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Broker Setup</Text>

      {status && status.status === 'connected' ? (
        <View style={styles.statusCard}>
          <Text style={styles.statusTitle}>Connected</Text>
          <Text style={styles.statusText}>Broker: {status.broker_name}</Text>
          <Text style={styles.statusText}>{status.message}</Text>
          <TouchableOpacity
            style={styles.disconnectButton}
            onPress={handleDisconnect}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.buttonText}>Disconnect</Text>
            )}
          </TouchableOpacity>
        </View>
      ) : (
        <View style={styles.form}>
          <Text style={styles.label}>Select Broker</Text>
          <View style={styles.pickerContainer}>
            <Picker
              selectedValue={selectedBroker}
              onValueChange={setSelectedBroker}
              style={styles.picker}
            >
              {brokers.map((broker) => (
                <Picker.Item
                  key={broker}
                  label={broker.charAt(0).toUpperCase() + broker.slice(1)}
                  value={broker}
                />
              ))}
            </Picker>
          </View>

          <Text style={styles.label}>API Key</Text>
          <TextInput
            style={styles.input}
            placeholder="Enter your API key"
            value={apiKey}
            onChangeText={setApiKey}
            autoCapitalize="none"
          />

          <Text style={styles.label}>API Secret</Text>
          <TextInput
            style={styles.input}
            placeholder="Enter your API secret"
            value={apiSecret}
            onChangeText={setApiSecret}
            secureTextEntry
          />

          <TouchableOpacity
            style={styles.button}
            onPress={handleConnect}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.buttonText}>Connect Broker</Text>
            )}
          </TouchableOpacity>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#333',
  },
  form: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 5,
    color: '#333',
  },
  input: {
    backgroundColor: '#f9f9f9',
    padding: 15,
    borderRadius: 10,
    marginBottom: 15,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  pickerContainer: {
    backgroundColor: '#f9f9f9',
    borderRadius: 10,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  picker: {
    height: 50,
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 10,
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  statusCard: {
    backgroundColor: '#e8f5e9',
    padding: 20,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#81c784',
  },
  statusTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2e7d32',
    marginBottom: 10,
  },
  statusText: {
    fontSize: 16,
    color: '#333',
    marginBottom: 5,
  },
  disconnectButton: {
    backgroundColor: '#f44336',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 15,
  },
});
