import React, { useState, useEffect } from 'react';
import { Plus, Trash2, Download, TrendingDown, TrendingUp, Calendar, DollarSign, LogOut, Users } from 'lucide-react';

export default function ExpenseTracker() {
  const [currentUser, setCurrentUser] = useState(null);
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [activeTab, setActiveTab] = useState('revenues');
  
  // Formulaire dépenses
  const [expenseDesc, setExpenseDesc] = useState('');
  const [expenseAmount, setExpenseAmount] = useState('');
  const [expenseCategory, setExpenseCategory] = useState('Manettes PC');
  const [expenseDate, setExpenseDate] = useState(new Date().toISOString().split('T')[0]);
  
  // Formulaire revenus
  const [revenueDesc, setRevenueDesc] = useState('');
  const [revenueAmount, setRevenueAmount] = useState('');
  const [revenueType, setRevenueType] = useState('Vente manette');
  const [revenueDate, setRevenueDate] = useState(new Date().toISOString().split('T')[0]);
  
  const [expenses, setExpenses] = useState([]);
  const [revenues, setRevenues] = useState([]);
  const [notification, setNotification] = useState(null);

  const users = {
    'conakry1@rotagaming.gn': { id: 'conakry1', name: 'Agent Conakry 1', location: 'Conakry', password: 'rotagaming2026' },
    'conakry2@rotagaming.gn': { id: 'conakry2', name: 'Agent Conakry 2', location: 'Conakry', password: 'rotagaming2026' },
    'mamou1@rotagaming.gn': { id: 'mamou1', name: 'Agent Mamou 1', location: 'Mamou', password: 'rotagaming2026' },
    'mamou2@rotagaming.gn': { id: 'mamou2', name: 'Agent Mamou 2', location: 'Mamou', password: 'rotagaming2026' },
    'admin@rotagaming.gn': { id: 'admin', name: 'Administrateur', location: 'Direction', password: 'rotagaming2026' }
  };

  const expenseCategories = [
    'Manettes PC', 'Jeux PC', 'Matériel informatique', 'Logiciels',
    'Transport/Déplacement', 'Internet/Abonnements', 'Publicité',
    'Fournitures bureau', 'Autre'
  ];

  const revenueTypes = [
    'Vente manette', 'Installation jeu PC', 'Configuration PC gaming',
    'Maintenance/Support', 'Accessoires gaming', 'Autre'
  ];

  // Charger les données au login
  useEffect(() => {
    if (currentUser) {
      loadUserData();
    }
  }, [currentUser]);

  const loadUserData = async () => {
    try {
      const expensesResult = await window.storage.get(`${currentUser.id}_expenses`, true);
      const revenuesResult = await window.storage.get(`${currentUser.id}_revenues`, true);
      
      if (expensesResult?.value) {
        setExpenses(JSON.parse(expensesResult.value));
      } else {
        setExpenses([]);
      }
      
      if (revenuesResult?.value) {
        setRevenues(JSON.parse(revenuesResult.value));
      } else {
        setRevenues([]);
      }
    } catch (error) {
      setExpenses([]);
      setRevenues([]);
    }
  };

  const saveExpenses = async (newExpenses) => {
    setExpenses(newExpenses);
    try {
      await window.storage.set(`${currentUser.id}_expenses`, JSON.stringify(newExpenses), true);
    } catch (error) {
      console.error('Erreur de sauvegarde:', error);
    }
  };

  const saveRevenues = async (newRevenues) => {
    setRevenues(newRevenues);
    try {
      await window.storage.set(`${currentUser.id}_revenues`, JSON.stringify(newRevenues), true);
    } catch (error) {
      console.error('Erreur de sauvegarde:', error);
    }
  };

  const login = () => {
    const user = users[loginEmail];
    
    if (user && user.password === loginPassword) {
      setCurrentUser(user);
      setLoginEmail('');
      setLoginPassword('');
      showNotification('✅ Connexion réussie !', 'success');
    } else {
      showNotification('❌ Email ou mot de passe incorrect', 'error');
    }
  };

  const logout = () => {
    setCurrentUser(null);
    setExpenses([]);
    setRevenues([]);
    setActiveTab('revenues');
    showNotification('👋 Déconnexion réussie', 'success');
  };

  const addExpense = async () => {
    if (expenseDesc && expenseAmount && parseFloat(expenseAmount) > 0) {
      const newExpense = {
        id: Date.now(),
        description: expenseDesc,
        amount: parseFloat(expenseAmount),
        category: expenseCategory,
        date: expenseDate
      };
      
      await saveExpenses([newExpense, ...expenses]);
      
      setExpenseDesc('');
      setExpenseAmount('');
      setExpenseDate(new Date().toISOString().split('T')[0]);
      showNotification('✅ Dépense ajoutée avec succès !', 'success');
    }
  };

  const addRevenue = async () => {
    if (revenueDesc && revenueAmount && parseFloat(revenueAmount) > 0) {
      const newRevenue = {
        id: Date.now(),
        description: revenueDesc,
        amount: parseFloat(revenueAmount),
        type: revenueType,
        date: revenueDate
      };
      
      await saveRevenues([newRevenue, ...revenues]);
      
      setRevenueDesc('');
      setRevenueAmount('');
      setRevenueDate(new Date().toISOString().split('T')[0]);
      showNotification('✅ Revenu ajouté avec succès !', 'success');
    }
  };

  const deleteExpense = async (id) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer cette dépense ?')) {
      await saveExpenses(expenses.filter(exp => exp.id !== id));
      showNotification('🗑️ Dépense supprimée', 'success');
    }
  };

  const deleteRevenue = async (id) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer ce revenu ?')) {
      await saveRevenues(revenues.filter(rev => rev.id !== id));
      showNotification('🗑️ Revenu supprimé', 'success');
    }
  };

  const totalExpenses = expenses.reduce((sum, exp) => sum + exp.amount, 0);
  const totalRevenues = revenues.reduce((sum, rev) => sum + rev.amount, 0);
  const profit = totalRevenues - totalExpenses;

  const currentMonth = new Date().toISOString().slice(0, 7);
  const monthlyExpenses = expenses.filter(exp => exp.date.startsWith(currentMonth)).reduce((sum, exp) => sum + exp.amount, 0);
  const monthlyRevenues = revenues.filter(rev => rev.date.startsWith(currentMonth)).reduce((sum, rev) => sum + rev.amount, 0);
  const monthlyProfit = monthlyRevenues - monthlyExpenses;

  const exportToCSV = () => {
    const headers = ['Type', 'Date', 'Description', 'Catégorie/Type', 'Montant'];
    const expenseRows = expenses.map(exp => ['Dépense', exp.date, exp.description, exp.category, `-${exp.amount}`]);
    const revenueRows = revenues.map(rev => ['Revenu', rev.date, rev.description, rev.type, rev.amount]);
    
    const csvContent = [headers.join(','), ...expenseRows.map(row => row.join(',')), ...revenueRows.map(row => row.join(','))].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `rotagaming_${currentUser.name.replace(/\s/g, '_')}_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  const showNotification = (message, type) => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  // Écran de connexion
  if (!currentUser) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center p-4">
        <div className="bg-white rounded-3xl shadow-2xl p-8 max-w-md w-full">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-800 mb-2">🎮 ROTAGAMING</h1>
            <p className="text-gray-600">Système de Gestion Comptable</p>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
              <input
                type="email"
                value={loginEmail}
                onChange={(e) => setLoginEmail(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && login(e)}
                placeholder="agent@rotagaming.gn"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Mot de passe</label>
              <input
                type="password"
                value={loginPassword}
                onChange={(e) => setLoginPassword(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && login(e)}
                placeholder="••••••••"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:outline-none"
              />
            </div>
            <button
              onClick={login}
              className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white font-bold py-3 rounded-lg hover:shadow-lg transition"
            >
              Se connecter
            </button>
          </div>

          <div className="mt-6 p-4 bg-blue-50 rounded-lg text-sm">
            <p className="font-bold text-gray-700 mb-2">📝 Comptes disponibles :</p>
            <p className="text-gray-600">• conakry1@rotagaming.gn</p>
            <p className="text-gray-600">• conakry2@rotagaming.gn</p>
            <p className="text-gray-600">• mamou1@rotagaming.gn</p>
            <p className="text-gray-600">• mamou2@rotagaming.gn</p>
            <p className="text-gray-600">• admin@rotagaming.gn</p>
            <p className="text-gray-500 mt-2 text-xs">Mot de passe : rotagaming2026</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-100 p-4">
      {notification && (
        <div className={`fixed top-4 right-4 z-50 ${notification.type === 'success' ? 'bg-green-500' : 'bg-red-500'} text-white px-6 py-4 rounded-lg shadow-lg`}>
          <span className="text-lg font-semibold">{notification.message}</span>
        </div>
      )}

      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-800 mb-2">🎮 ROTAGAMING - Gestion Comptable</h1>
              <p className="text-gray-600">Installation jeux PC & Vente de manettes</p>
            </div>
            <div className="text-right">
              <p className="font-bold text-gray-800">{currentUser.name}</p>
              <p className="text-sm text-gray-600">📍 {currentUser.location}</p>
              <button
                onClick={logout}
                className="mt-2 bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 text-sm transition-colors ml-auto"
              >
                <LogOut size={16} />
                Déconnexion
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-md p-6 text-white">
            <div className="flex items-center gap-3 mb-2">
              <TrendingUp size={24} />
              <h3 className="text-lg font-semibold">Revenus Total</h3>
            </div>
            <p className="text-3xl font-bold">{totalRevenues.toLocaleString('fr-FR')} GNF</p>
            <p className="text-sm opacity-90 mt-1">{revenues.length} vente(s)</p>
          </div>

          <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-xl shadow-md p-6 text-white">
            <div className="flex items-center gap-3 mb-2">
              <TrendingDown size={24} />
              <h3 className="text-lg font-semibold">Dépenses Total</h3>
            </div>
            <p className="text-3xl font-bold">{totalExpenses.toLocaleString('fr-FR')} GNF</p>
            <p className="text-sm opacity-90 mt-1">{expenses.length} dépense(s)</p>
          </div>

          <div className={`bg-gradient-to-br ${profit >= 0 ? 'from-blue-500 to-blue-600' : 'from-orange-500 to-orange-600'} rounded-xl shadow-md p-6 text-white`}>
            <div className="flex items-center gap-3 mb-2">
              <DollarSign size={24} />
              <h3 className="text-lg font-semibold">Bénéfice Net</h3>
            </div>
            <p className="text-3xl font-bold">{profit.toLocaleString('fr-FR')} GNF</p>
            <p className="text-sm opacity-90 mt-1">{profit >= 0 ? 'Positif' : 'Négatif'}</p>
          </div>

          <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-md p-6 text-white">
            <div className="flex items-center gap-3 mb-2">
              <Calendar size={24} />
              <h3 className="text-lg font-semibold">Ce Mois-ci</h3>
            </div>
            <p className="text-3xl font-bold">{monthlyProfit.toLocaleString('fr-FR')} GNF</p>
            <p className="text-sm opacity-90 mt-1">{new Date().toLocaleDateString('fr-FR', { month: 'long' })}</p>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
          <div className="flex gap-2 mb-6 border-b">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`px-6 py-3 font-semibold transition-colors ${activeTab === 'dashboard' ? 'border-b-2 border-purple-600 text-purple-600' : 'text-gray-600 hover:text-purple-600'}`}
            >
              📊 Tableau de bord
            </button>
            <button
              onClick={() => setActiveTab('revenues')}
              className={`px-6 py-3 font-semibold transition-colors ${activeTab === 'revenues' ? 'border-b-2 border-green-600 text-green-600' : 'text-gray-600 hover:text-green-600'}`}
            >
              💰 Revenus
            </button>
            <button
              onClick={() => setActiveTab('expenses')}
              className={`px-6 py-3 font-semibold transition-colors ${activeTab === 'expenses' ? 'border-b-2 border-red-600 text-red-600' : 'text-gray-600 hover:text-red-600'}`}
            >
              💸 Dépenses
            </button>
          </div>

          {activeTab === 'dashboard' && (
            <div>
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold text-gray-800">Vue d'ensemble</h2>
                <button
                  onClick={exportToCSV}
                  disabled={expenses.length === 0 && revenues.length === 0}
                  className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-semibold py-2 px-4 rounded-lg flex items-center gap-2 transition-colors"
                >
                  <Download size={18} />
                  Exporter CSV
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                <div className="border-2 border-gray-200 rounded-lg p-4">
                  <h3 className="font-bold text-gray-700 mb-3">📈 Chiffre d'affaires mensuel</h3>
                  <p className="text-2xl font-bold text-green-600">{monthlyRevenues.toLocaleString('fr-FR')} GNF</p>
                </div>
                
                <div className="border-2 border-gray-200 rounded-lg p-4">
                  <h3 className="font-bold text-gray-700 mb-3">📉 Charges mensuelles</h3>
                  <p className="text-2xl font-bold text-red-600">{monthlyExpenses.toLocaleString('fr-FR')} GNF</p>
                </div>
              </div>

              <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                <h3 className="font-bold text-gray-700 mb-2">💡 Résumé rapide</h3>
                <p className="text-gray-600">Total ventes : {revenues.length} | Total achats : {expenses.length}</p>
                <p className="text-gray-600 mt-1">Marge bénéficiaire : {totalRevenues > 0 ? ((profit / totalRevenues) * 100).toFixed(1) : 0}%</p>
              </div>
            </div>
          )}

          {activeTab === 'revenues' && (
            <div>
              <h2 className="text-xl font-bold text-gray-800 mb-4">➕ Ajouter un revenu</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <input
                  type="text"
                  value={revenueDesc}
                  onChange={(e) => setRevenueDesc(e.target.value)}
                  placeholder="Description"
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none"
                />
                <input
                  type="number"
                  value={revenueAmount}
                  onChange={(e) => setRevenueAmount(e.target.value)}
                  placeholder="Montant (GNF)"
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none"
                />
                <select
                  value={revenueType}
                  onChange={(e) => setRevenueType(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none"
                >
                  {revenueTypes.map(type => <option key={type} value={type}>{type}</option>)}
                </select>
                <input
                  type="date"
                  value={revenueDate}
                  onChange={(e) => setRevenueDate(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none"
                />
              </div>

              <button
                onClick={addRevenue}
                className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded-lg mb-6 flex items-center justify-center gap-2"
              >
                <Plus size={20} />
                Ajouter le revenu
              </button>

              <div className="space-y-3">
                {revenues.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    <p className="text-lg">Aucun revenu enregistré</p>
                  </div>
                ) : (
                  revenues.map(revenue => (
                    <div key={revenue.id} className="flex items-center justify-between p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-1">
                          <span className="font-semibold text-gray-800">{revenue.description}</span>
                          <span className="px-2 py-1 bg-green-200 text-green-800 text-xs rounded-full">{revenue.type}</span>
                        </div>
                        <p className="text-sm text-gray-500">{new Date(revenue.date).toLocaleDateString('fr-FR')}</p>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="text-xl font-bold text-green-700">+{revenue.amount.toLocaleString('fr-FR')} GNF</span>
                        <button onClick={() => deleteRevenue(revenue.id)} className="text-red-500 hover:text-red-700">
                          <Trash2 size={20} />
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {activeTab === 'expenses' && (
            <div>
              <h2 className="text-xl font-bold text-gray-800 mb-4">➕ Ajouter une dépense</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <input
                  type="text"
                  value={expenseDesc}
                  onChange={(e) => setExpenseDesc(e.target.value)}
                  placeholder="Description"
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                />
                <input
                  type="number"
                  value={expenseAmount}
                  onChange={(e) => setExpenseAmount(e.target.value)}
                  placeholder="Montant (GNF)"
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                />
                <select
                  value={expenseCategory}
                  onChange={(e) => setExpenseCategory(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                >
                  {expenseCategories.map(cat => <option key={cat} value={cat}>{cat}</option>)}
                </select>
                <input
                  type="date"
                  value={expenseDate}
                  onChange={(e) => setExpenseDate(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:outline-none"
                />
              </div>

              <button
                onClick={addExpense}
                className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 rounded-lg mb-6 flex items-center justify-center gap-2"
              >
                <Plus size={20} />
                Ajouter la dépense
              </button>

              <div className="space-y-3">
                {expenses.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    <p className="text-lg">Aucune dépense enregistrée</p>
                  </div>
                ) : (
                  expenses.map(expense => (
                    <div key={expense.id} className="flex items-center justify-between p-4 bg-red-50 rounded-lg hover:bg-red-100 transition-colors">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-1">
                          <span className="font-semibold text-gray-800">{expense.description}</span>
                          <span className="px-2 py-1 bg-red-200 text-red-800 text-xs rounded-full">{expense.category}</span>
                        </div>
                        <p className="text-sm text-gray-500">{new Date(expense.date).toLocaleDateString('fr-FR')}</p>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="text-xl font-bold text-red-700">-{expense.amount.toLocaleString('fr-FR')} GNF</span>
                        <button onClick={() => deleteExpense(expense.id)} className="text-red-500 hover:text-red-700">
                          <Trash2 size={20} />
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
