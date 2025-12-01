import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  FlatList,
  Alert,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { strategyService } from '../services/strategies';
import { Strategy } from '../types';

interface StrategyManagementScreenProps {
  userId: string;
}

export default function StrategyManagementScreen({ userId }: StrategyManagementScreenProps) {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadStrategies();
  }, []);

  const loadStrategies = async () => {
    try {
      const data = await strategyService.list(userId);
      setStrategies(data);
    } catch (error) {
      console.error('Failed to load strategies:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleStartStop = async (strategy: Strategy) => {
    try {
      if (strategy.status === 'active') {
        await strategyService.stop(strategy.id);
        Alert.alert('Success', 'Strategy stopped');
      } else {
        await strategyService.start(strategy.id);
        Alert.alert('Success', 'Strategy started');
      }
      loadStrategies();
    } catch (error: any) {
      Alert.alert(
        'Error',
        error.response?.data?.detail || 'Failed to update strategy'
      );
    }
  };

  const handleDelete = (strategy: Strategy) => {
    Alert.alert(
      'Delete Strategy',
      `Are you sure you want to delete "${strategy.name}"?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await strategyService.delete(strategy.id);
              loadStrategies();
            } catch (error: any) {
              Alert.alert(
                'Error',
                error.response?.data?.detail || 'Failed to delete strategy'
              );
            }
          },
        },
      ]
    );
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return '#4caf50';
      case 'paused':
        return '#ff9800';
      case 'stopped':
        return '#9e9e9e';
      default:
        return '#9e9e9e';
    }
  };

  const renderStrategy = ({ item }: { item: Strategy }) => (
    <View style={styles.card}>
      <View style={styles.cardHeader}>
        <Text style={styles.strategyName}>{item.name}</Text>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.status) }]}>
          <Text style={styles.statusText}>{item.status.toUpperCase()}</Text>
        </View>
      </View>

      <View style={styles.cardBody}>
        <Text style={styles.detailText}>Type: {item.strategy_type.replace('_', ' ')}</Text>
        <Text style={styles.detailText}>Symbol: {item.symbol}</Text>
      </View>

      <View style={styles.cardActions}>
        <TouchableOpacity
          style={[styles.actionButton, item.status === 'active' ? styles.stopButton : styles.startButton]}
          onPress={() => handleStartStop(item)}
        >
          <Text style={styles.actionButtonText}>
            {item.status === 'active' ? 'Stop' : 'Start'}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.actionButton, styles.deleteButton]}
          onPress={() => handleDelete(item)}
        >
          <Text style={styles.actionButtonText}>Delete</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Strategies</Text>

      {strategies.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>No strategies yet</Text>
          <Text style={styles.emptySubtext}>
            Create a strategy from the backend API to get started
          </Text>
        </View>
      ) : (
        <FlatList
          data={strategies}
          renderItem={renderStrategy}
          keyExtractor={(item) => item.id}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={() => {
              setRefreshing(true);
              loadStrategies();
            }} />
          }
          contentContainerStyle={styles.listContainer}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    padding: 20,
    color: '#333',
  },
  listContainer: {
    padding: 15,
    paddingTop: 0,
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 15,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  strategyName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  cardBody: {
    marginBottom: 15,
  },
  detailText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
    textTransform: 'capitalize',
  },
  cardActions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: 10,
  },
  actionButton: {
    paddingHorizontal: 20,
    paddingVertical: 8,
    borderRadius: 5,
  },
  startButton: {
    backgroundColor: '#4caf50',
  },
  stopButton: {
    backgroundColor: '#ff9800',
  },
  deleteButton: {
    backgroundColor: '#f44336',
  },
  actionButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#666',
    marginBottom: 10,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
  },
});
