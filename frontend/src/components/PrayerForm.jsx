import React, { useState } from 'react';
import { Plus, User, Clock, MessageCircle } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { RadioGroup, RadioGroupItem } from '../components/ui/radio-group';

const PrayerForm = ({ onAddPrayer }) => {
  const [formData, setFormData] = useState({
    name: '',
    time: '',
    timeUnit: 'minutes',
    description: '',
  });
  const [errors, setErrors] = useState({});

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.name.trim()) {
      newErrors.name = 'Nome é obrigatório';
    }
    
    if (!formData.time || parseInt(formData.time) <= 0) {
      newErrors.time = 'Tempo deve ser maior que zero';
    }

    return newErrors;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const newErrors = validateForm();
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    const prayerData = {
      ...formData,
      time: parseInt(formData.time)
    };

    onAddPrayer(prayerData);
    
    // Reset form
    setFormData({
      name: '',
      time: '',
      timeUnit: 'minutes',
      description: '',
    });
    setErrors({});
  };

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-4 sm:p-8 shadow-xl border border-gray-200">
      <div className="mb-4 sm:mb-6">
        <div className="inline-flex items-center gap-2 mb-2">
          <Plus className="w-5 h-5 sm:w-6 sm:h-6 text-emerald-600" />
          <h2 className="text-xl sm:text-2xl font-bold text-gray-800">Adicionar Oração</h2>
        </div>
        <p className="text-sm sm:text-base text-gray-600">Registre seu tempo de oração</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-6">
        {/* Name Field */}
        <div className="space-y-2">
          <Label htmlFor="name" className="flex items-center gap-2 text-gray-700 text-sm sm:text-base">
            <User className="w-4 h-4" />
            Nome *
          </Label>
          <Input
            id="name"
            type="text"
            placeholder="Seu nome"
            value={formData.name}
            onChange={(e) => handleInputChange('name', e.target.value)}
            className={`transition-colors text-sm sm:text-base ${errors.name ? 'border-red-500' : 'border-gray-300 focus:border-emerald-500'}`}
          />
          {errors.name && (
            <p className="text-red-500 text-xs sm:text-sm mt-1">{errors.name}</p>
          )}
        </div>

        {/* Time Field */}
        <div className="space-y-2">
          <Label htmlFor="time" className="flex items-center gap-2 text-gray-700 text-sm sm:text-base">
            <Clock className="w-4 h-4" />
            Tempo de Oração *
          </Label>
          <div className="flex flex-col sm:flex-row gap-3">
            <Input
              id="time"
              type="number"
              min="1"
              placeholder="0"
              value={formData.time}
              onChange={(e) => handleInputChange('time', e.target.value)}
              className={`flex-1 transition-colors text-sm sm:text-base ${errors.time ? 'border-red-500' : 'border-gray-300 focus:border-emerald-500'}`}
            />
            <RadioGroup
              value={formData.timeUnit}
              onValueChange={(value) => handleInputChange('timeUnit', value)}
              className="flex gap-4 sm:gap-6 justify-center sm:justify-start"
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="minutes" id="minutes" />
                <Label htmlFor="minutes" className="text-sm">Minutos</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="hours" id="hours" />
                <Label htmlFor="hours" className="text-sm">Horas</Label>
              </div>
            </RadioGroup>
          </div>
          {errors.time && (
            <p className="text-red-500 text-xs sm:text-sm mt-1">{errors.time}</p>
          )}
        </div>

        {/* Description Field */}
        <div className="space-y-2">
          <Label htmlFor="description" className="flex items-center gap-2 text-gray-700 text-sm sm:text-base">
            <MessageCircle className="w-4 h-4" />
            Motivo/Descrição (opcional)
          </Label>
          <Textarea
            id="description"
            placeholder="Pelo que você orou? (opcional)"
            value={formData.description}
            onChange={(e) => handleInputChange('description', e.target.value)}
            rows={3}
            className="transition-colors border-gray-300 focus:border-emerald-500 resize-none text-sm sm:text-base"
          />
        </div>

        {/* Submit Button */}
        <Button
          type="submit"
          className="w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-semibold py-2 sm:py-3 px-6 rounded-lg transition-all duration-200 transform hover:scale-[1.02] shadow-lg text-sm sm:text-base"
        >
          <Plus className="w-4 h-4 sm:w-5 sm:h-5 mr-2" />
          Registrar Oração
        </Button>
      </form>
    </div>
  );
};

export default PrayerForm;