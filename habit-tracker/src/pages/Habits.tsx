import React, { useState } from 'react';
import { Plus, Target, RefreshCw, Search } from 'lucide-react';
import { HabitCard } from '../components/HabitCard';
import { Modal } from '../components/Modal';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { useHabits } from '../hooks/useHabits';
import { useCheckIns } from '../hooks/useCheckIns';
import { useDataValidation } from '../hooks/useDataValidation';
import type { Frequency, Habit } from '../types';
import { validateHabit } from '../utils/validator';
import { cn } from '../lib/utils';

const colorOptions = [
  '#0ea5e9', '#10b981', '#f59e0b', '#f43f5e',
  '#8b5cf6', '#ec4899', '#f97316', '#06b6d4',
];

const Habits: React.FC = () => {
  const { habitsWithStats, addHabit, updateHabit, dailyHabits, weeklyHabits } = useHabits();
  const { checkIn, uncheck } = useCheckIns();
  const { validateSingleHabit } = useDataValidation();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingHabit, setEditingHabit] = useState<Habit | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<'all' | 'daily' | 'weekly'>('all');

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    frequency: 'daily' as Frequency,
    targetCount: 1,
    color: '#0ea5e9',
  });
  const [formErrors, setFormErrors] = useState<string[]>([]);

  const openModal = (habit?: Habit) => {
    if (habit) {
      setEditingHabit(habit);
      setFormData({
        name: habit.name,
        description: habit.description,
        frequency: habit.frequency,
        targetCount: habit.targetCount,
        color: habit.color,
      });
    } else {
      setEditingHabit(null);
      setFormData({
        name: '',
        description: '',
        frequency: 'daily',
        targetCount: 1,
        color: '#0ea5e9',
      });
    }
    setFormErrors([]);
    setIsModalOpen(true);
  };

  const handleSubmit = () => {
    const validation = validateHabit(formData);
    if (!validation.valid) {
      setFormErrors(validation.errors);
      return;
    }

    if (editingHabit) {
      updateHabit(editingHabit.id, formData);
    } else {
      addHabit(formData);
    }

    setIsModalOpen(false);
  };

  const filteredHabits = habitsWithStats.filter(item => {
    const matchesSearch = item.habit.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesTab = activeTab === 'all'
      ? true
      : activeTab === 'daily'
      ? item.habit.frequency === 'daily'
      : item.habit.frequency === 'weekly';
    return matchesSearch && matchesTab;
  });

  const displayHabits = activeTab === 'all'
    ? filteredHabits
    : activeTab === 'daily'
    ? filteredHabits
    : filteredHabits;

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-zinc-900 dark:text-white">
            习惯管理
          </h1>
          <p className="text-zinc-500 dark:text-zinc-400 mt-2">
            管理你的习惯，追踪每日进度
          </p>
        </div>

        <button
          onClick={() => openModal()}
          className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-sky-500 to-cyan-500 text-white font-semibold rounded-xl shadow-lg shadow-sky-500/25 hover:shadow-xl hover:shadow-sky-500/30 transition-all duration-300 hover:-translate-y-0.5"
        >
          <Plus className="w-5 h-5" />
          添加习惯
        </button>
      </div>

      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-400" />
          <input
            type="text"
            placeholder="搜索习惯..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-12 pr-4 py-3 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-sky-500 text-zinc-900 dark:text-white placeholder-zinc-400"
          />
        </div>

        <div className="flex gap-2 bg-white dark:bg-zinc-900 p-1 rounded-xl border border-zinc-200 dark:border-zinc-800">
          {(['all', 'daily', 'weekly'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={cn(
                'px-4 py-2 rounded-lg font-medium transition-all duration-200',
                activeTab === tab
                  ? 'bg-sky-500 text-white shadow-md'
                  : 'text-zinc-500 hover:text-zinc-900 dark:hover:text-white'
              )}
            >
              {tab === 'all' ? '全部' : tab === 'daily' ? '每日' : '每周'}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-sky-50 dark:bg-sky-900/20 rounded-2xl p-4 border border-sky-100 dark:border-sky-800">
          <div className="flex items-center gap-2 mb-2">
            <Target className="w-5 h-5 text-sky-500" />
            <span className="font-semibold text-sky-700 dark:text-sky-400">每日习惯</span>
            <span className="ml-auto bg-sky-500 text-white text-xs px-2 py-1 rounded-full">
              {dailyHabits.length}
            </span>
          </div>
        </div>
        <div className="bg-purple-50 dark:bg-purple-900/20 rounded-2xl p-4 border border-purple-100 dark:border-purple-800">
          <div className="flex items-center gap-2 mb-2">
            <RefreshCw className="w-5 h-5 text-purple-500" />
            <span className="font-semibold text-purple-700 dark:text-purple-400">每周习惯</span>
            <span className="ml-auto bg-purple-500 text-white text-xs px-2 py-1 rounded-full">
              {weeklyHabits.length}
            </span>
          </div>
        </div>
      </div>

      {displayHabits.length === 0 ? (
        <div className="bg-white dark:bg-zinc-900 rounded-2xl p-12 text-center border border-zinc-100 dark:border-zinc-800">
          <Target className="w-16 h-16 text-zinc-300 dark:text-zinc-700 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-zinc-900 dark:text-white mb-2">
            {searchQuery ? '没有找到匹配的习惯' : '还没有添加习惯'}
          </h3>
          <p className="text-zinc-500 dark:text-zinc-400 mb-4">
            {searchQuery ? '试试其他关键词' : '点击上方按钮创建你的第一个习惯'}
          </p>
          {!searchQuery && (
            <button
              onClick={() => openModal()}
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-sky-500 to-cyan-500 text-white font-semibold rounded-xl hover:shadow-lg transition-all duration-300"
            >
              <Plus className="w-5 h-5" />
              添加习惯
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {displayHabits.map((item, index) => (
            <div key={item.habit.id} style={{ animationDelay: `${index * 100}ms` }}>
              <HabitCard
                habit={item.habit}
                stats={item.stats}
                isCheckedInToday={item.isCheckedInToday}
                weeklyCount={item.weeklyCount}
                onEdit={() => openModal(item.habit)}
              />
            </div>
          ))}
        </div>
      )}

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingHabit ? '编辑习惯' : '添加新习惯'}
        size="lg"
      >
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
              习惯名称 *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="例如：早起、运动、阅读..."
              className="w-full px-4 py-3 bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-sky-500 text-zinc-900 dark:text-white placeholder-zinc-400"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
              描述
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="为什么要养成这个习惯？"
              rows={3}
              className="w-full px-4 py-3 bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-sky-500 text-zinc-900 dark:text-white placeholder-zinc-400 resize-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                频率 *
              </label>
              <select
                value={formData.frequency}
                onChange={(e) => setFormData({
                  ...formData,
                  frequency: e.target.value as Frequency,
                  targetCount: e.target.value === 'daily' ? 1 : 3,
                })}
                className="w-full px-4 py-3 bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-sky-500 text-zinc-900 dark:text-white"
              >
                <option value="daily">每日</option>
                <option value="weekly">每周</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                {formData.frequency === 'daily' ? '每日目标' : '每周目标次数'} *
              </label>
              {formData.frequency === 'daily' ? (
                <div className="px-4 py-3 bg-zinc-50 dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-xl text-zinc-500">
                  每天 1 次
                </div>
              ) : (
                <select
                  value={formData.targetCount}
                  onChange={(e) => setFormData({ ...formData, targetCount: Number(e.target.value) })}
                  className="w-full px-4 py-3 bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-sky-500 text-zinc-900 dark:text-white"
                >
                  {[1, 2, 3, 4, 5, 6, 7].map(n => (
                    <option key={n} value={n}>每周 {n} 次</option>
                  ))}
                </select>
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
              主题色
            </label>
            <div className="flex gap-3 flex-wrap">
              {colorOptions.map(color => (
                <button
                  key={color}
                  onClick={() => setFormData({ ...formData, color })}
                  className={cn(
                    'w-10 h-10 rounded-xl transition-all duration-200',
                    formData.color === color && 'ring-4 ring-offset-2 dark:ring-offset-zinc-900 scale-110'
                  )}
                  style={{ backgroundColor: color }}
                />
              ))}
            </div>
          </div>

          {formErrors.length > 0 && (
            <div className="bg-rose-50 dark:bg-rose-900/20 border border-rose-200 dark:border-rose-800 rounded-xl p-4">
              <ul className="list-disc list-inside text-rose-600 dark:text-rose-400 text-sm space-y-1">
                {formErrors.map((error, i) => (
                  <li key={i}>{error}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="flex gap-3 pt-4">
            <button
              onClick={() => setIsModalOpen(false)}
              className="flex-1 px-6 py-3 bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 font-semibold rounded-xl hover:bg-zinc-200 dark:hover:bg-zinc-700 transition-colors"
            >
              取消
            </button>
            <button
              onClick={handleSubmit}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-sky-500 to-cyan-500 text-white font-semibold rounded-xl shadow-lg shadow-sky-500/25 hover:shadow-xl hover:shadow-sky-500/30 transition-all duration-300"
            >
              {editingHabit ? '保存修改' : '创建习惯'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default Habits;
