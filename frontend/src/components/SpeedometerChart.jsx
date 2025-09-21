import React, { useEffect, useRef } from 'react';
import { TrendingUp } from 'lucide-react';

const SpeedometerChart = ({ totalHours }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    // Make canvas responsive
    const container = canvas.parentElement;
    const containerWidth = container.clientWidth;
    const isMobile = window.innerWidth < 640;
    
    const canvasWidth = Math.min(containerWidth - 32, isMobile ? 320 : 400);
    const canvasHeight = isMobile ? 180 : 250;
    
    canvas.width = canvasWidth;
    canvas.height = canvasHeight;

    const ctx = canvas.getContext('2d');
    const centerX = canvas.width / 2;
    const centerY = canvas.height - (isMobile ? 30 : 50);
    const radius = Math.min(canvas.width, canvas.height) * (isMobile ? 0.4 : 0.35);

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw speedometer arc with gradient
    const gradient = ctx.createLinearGradient(centerX - radius, centerY, centerX + radius, centerY);
    gradient.addColorStop(0, '#ef4444'); // Red
    gradient.addColorStop(0.5, '#eab308'); // Yellow
    gradient.addColorStop(1, '#22c55e'); // Green

    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, Math.PI, 0);
    ctx.lineWidth = isMobile ? 18 : 25;
    ctx.strokeStyle = gradient;
    ctx.lineCap = 'round';
    ctx.stroke();

    // Draw background arc
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, Math.PI, 0);
    ctx.lineWidth = isMobile ? 22 : 30;
    ctx.strokeStyle = '#f1f5f9';
    ctx.globalCompositeOperation = 'destination-over';
    ctx.stroke();
    ctx.globalCompositeOperation = 'source-over';

    // Draw markers and labels
    const maxHours = 1000;
    for (let i = 0; i <= 10; i++) {
      const angle = Math.PI + (i / 10) * Math.PI;
      const markerLength = i % 5 === 0 ? (isMobile ? 10 : 15) : (isMobile ? 6 : 8);
      const textRadius = radius + (isMobile ? 25 : 35);
      
      // Marker lines
      const startX = centerX + Math.cos(angle) * (radius - markerLength);
      const startY = centerY + Math.sin(angle) * (radius - markerLength);
      const endX = centerX + Math.cos(angle) * radius;
      const endY = centerY + Math.sin(angle) * radius;
      
      ctx.beginPath();
      ctx.moveTo(startX, startY);
      ctx.lineTo(endX, endY);
      ctx.lineWidth = 2;
      ctx.strokeStyle = '#64748b';
      ctx.stroke();
      
      // Labels (show fewer labels on mobile)
      if ((!isMobile && i % 2 === 0) || (isMobile && i % 5 === 0)) {
        const labelX = centerX + Math.cos(angle) * textRadius;
        const labelY = centerY + Math.sin(angle) * textRadius;
        const hours = (i / 10) * maxHours;
        
        ctx.fillStyle = '#475569';
        ctx.font = `${isMobile ? '10' : '12'}px Inter, system-ui, sans-serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(hours.toString(), labelX, labelY);
      }
    }

    // Calculate needle position
    const progress = Math.min(totalHours / maxHours, 1);
    const needleAngle = Math.PI + progress * Math.PI;
    
    // Draw needle
    const needleLength = radius * 0.8;
    const needleX = centerX + Math.cos(needleAngle) * needleLength;
    const needleY = centerY + Math.sin(needleAngle) * needleLength;
    
    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.lineTo(needleX, needleY);
    ctx.lineWidth = isMobile ? 3 : 4;
    ctx.strokeStyle = '#1e293b';
    ctx.lineCap = 'round';
    ctx.stroke();
    
    // Draw center circle
    ctx.beginPath();
    ctx.arc(centerX, centerY, isMobile ? 6 : 8, 0, 2 * Math.PI);
    ctx.fillStyle = '#1e293b';
    ctx.fill();

    // Draw current hours text
    ctx.fillStyle = '#1e293b';
    ctx.font = `bold ${isMobile ? '18' : '24'}px Inter, system-ui, sans-serif`;
    ctx.textAlign = 'center';
    ctx.fillText(`${totalHours.toFixed(1)}h`, centerX, centerY + (isMobile ? 30 : 40));
    
    ctx.fillStyle = '#64748b';
    ctx.font = `${isMobile ? '12' : '14'}px Inter, system-ui, sans-serif`;
    ctx.fillText(`${(progress * 100).toFixed(1)}% da meta`, centerX, centerY + (isMobile ? 45 : 60));

  }, [totalHours]);

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-4 sm:p-8 shadow-xl border border-gray-200">
      <div className="text-center mb-4 sm:mb-6">
        <div className="inline-flex items-center gap-2 mb-2">
          <TrendingUp className="w-5 h-5 sm:w-6 sm:h-6 text-emerald-600" />
          <h2 className="text-xl sm:text-2xl font-bold text-gray-800">Progresso das Orações</h2>
        </div>
        <p className="text-sm sm:text-base text-gray-600">Velocímetro de horas acumuladas</p>
      </div>

      <div className="flex justify-center overflow-hidden">
        <canvas
          ref={canvasRef}
          className="max-w-full h-auto"
        />
      </div>

      <div className="flex justify-center mt-2 sm:mt-4">
        <div className="flex items-center gap-3 sm:gap-6 text-xs sm:text-sm flex-wrap justify-center">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 sm:w-3 sm:h-3 bg-red-500 rounded-full"></div>
            <span className="text-gray-600">0-300h</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 sm:w-3 sm:h-3 bg-yellow-500 rounded-full"></div>
            <span className="text-gray-600">300-700h</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 sm:w-3 sm:h-3 bg-green-500 rounded-full"></div>
            <span className="text-gray-600">700-1000h</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SpeedometerChart;