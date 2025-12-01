import React, { useState, useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';

import LoginScreen from './app/LoginScreen';
import BrokerSetupScreen from './app/BrokerSetupScreen';
import StrategyManagementScreen from './app/StrategyManagementScreen';
import { authService } from './services/api';

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

function MainTabs({ userId }: { userId: string }) {
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: '#999',
        headerShown: true,
      }}
    >
      <Tab.Screen
        name="Strategies"
        options={{
          tabBarLabel: 'Strategies',
          headerTitle: 'My Strategies',
        }}
      >
        {() => <StrategyManagementScreen userId={userId} />}
      </Tab.Screen>
      <Tab.Screen
        name="Broker"
        options={{
          tabBarLabel: 'Broker',
          headerTitle: 'Broker Setup',
        }}
      >
        {() => <BrokerSetupScreen userId={userId} />}
      </Tab.Screen>
    </Tab.Navigator>
  );
}

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const [userId, setUserId] = useState<string>('demo-user');

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const authenticated = await authService.isAuthenticated();
    setIsAuthenticated(authenticated);
    if (authenticated) {
      try {
        const user = await authService.getCurrentUser();
        setUserId(user.email);
      } catch {
        setIsAuthenticated(false);
      }
    }
  };

  const handleLoginSuccess = async () => {
    try {
      const user = await authService.getCurrentUser();
      setUserId(user.email);
      setIsAuthenticated(true);
    } catch {
      setIsAuthenticated(true);
    }
  };

  const handleLogout = async () => {
    await authService.logout();
    setIsAuthenticated(false);
  };

  if (isAuthenticated === null) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  return (
    <NavigationContainer>
      <StatusBar style="auto" />
      {isAuthenticated ? (
        <MainTabs userId={userId} />
      ) : (
        <Stack.Navigator screenOptions={{ headerShown: false }}>
          <Stack.Screen name="Login">
            {() => (
              <LoginScreen
                onLoginSuccess={handleLoginSuccess}
                onNavigateToRegister={() => {}}
              />
            )}
          </Stack.Screen>
        </Stack.Navigator>
      )}
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
});
