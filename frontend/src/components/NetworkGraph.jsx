/**
 * 網絡圖組件
 * Network Graph Component - 使用 D3.js 繪製力導向圖
 */

import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

export default function NetworkGraph({ data, onNodeClick }) {
  const svgRef = useRef();
  const containerRef = useRef();

  useEffect(() => {
    if (!data || !data.nodes || data.nodes.length === 0) {
      return;
    }

    // 清空之前的內容
    d3.select(svgRef.current).selectAll('*').remove();

    // 獲取容器尺寸
    const container = containerRef.current;
    const width = container.clientWidth;
    const height = 600;

    // 創建 SVG
    const svg = d3
      .select(svgRef.current)
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', [0, 0, width, height]);

    // 創建力導向模擬
    const simulation = d3
      .forceSimulation(data.nodes)
      .force(
        'link',
        d3
          .forceLink(data.links)
          .id((d) => d.id)
          .distance(100)
          .strength(0.5)
      )
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(30));

    // 創建縮放行為
    const zoom = d3.zoom()
      .scaleExtent([0.5, 3])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom);

    // 創建主容器
    const g = svg.append('g');

    // 繪製連線
    const link = g
      .append('g')
      .selectAll('line')
      .data(data.links)
      .join('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', (d) => Math.sqrt(d.weight || 1));

    // 繪製節點
    const node = g
      .append('g')
      .selectAll('circle')
      .data(data.nodes)
      .join('circle')
      .attr('r', (d) => {
        // 根據論文數量調整節點大小
        const baseSize = 5;
        const size = baseSize + Math.sqrt(d.papers_count || 1) * 2;
        return Math.min(size, 20); // 最大半徑 20
      })
      .attr('fill', (d) => {
        // 關鍵人物使用不同顏色
        if (d.is_key_person) {
          return '#f59e0b'; // 琥珀色
        }
        return '#3b82f6'; // 藍色
      })
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .on('click', (event, d) => {
        event.stopPropagation();
        if (onNodeClick) {
          onNodeClick(d.id);
        }
      })
      .on('mouseover', function (event, d) {
        // 高亮節點
        d3.select(this)
          .transition()
          .duration(200)
          .attr('r', (d) => {
            const baseSize = 5;
            const size = baseSize + Math.sqrt(d.papers_count || 1) * 2;
            return Math.min(size, 20) * 1.3;
          })
          .attr('stroke-width', 3);

        // 顯示提示
        tooltip
          .style('opacity', 1)
          .html(
            `
            <div class="font-semibold">${d.name}</div>
            <div class="text-xs mt-1">論文: ${d.papers_count || 0}</div>
            <div class="text-xs">引用: ${d.citations || 0}</div>
            <div class="text-xs">第一作者: ${d.first_author_count || 0}</div>
            ${d.is_key_person ? '<div class="text-xs text-yellow-600 font-semibold mt-1">關鍵人物</div>' : ''}
          `
          )
          .style('left', event.pageX + 10 + 'px')
          .style('top', event.pageY - 10 + 'px');
      })
      .on('mouseout', function (event, d) {
        // 恢復節點
        d3.select(this)
          .transition()
          .duration(200)
          .attr('r', (d) => {
            const baseSize = 5;
            const size = baseSize + Math.sqrt(d.papers_count || 1) * 2;
            return Math.min(size, 20);
          })
          .attr('stroke-width', 2);

        // 隱藏提示
        tooltip.style('opacity', 0);
      })
      .call(
        d3
          .drag()
          .on('start', dragStarted)
          .on('drag', dragged)
          .on('end', dragEnded)
      );

    // 繪製標籤（只為關鍵人物或論文數較多的作者顯示）
    const label = g
      .append('g')
      .selectAll('text')
      .data(data.nodes)
      .join('text')
      .text((d) => {
        // 只顯示關鍵人物或論文數 >= 3 的作者名字
        if (d.is_key_person || (d.papers_count || 0) >= 3) {
          // 顯示姓氏（假設是最後一個單詞）
          const parts = d.name.split(' ');
          return parts[parts.length - 1];
        }
        return '';
      })
      .attr('font-size', 10)
      .attr('dx', 12)
      .attr('dy', 4)
      .attr('fill', '#374151')
      .style('pointer-events', 'none');

    // 創建提示框
    const tooltip = d3
      .select('body')
      .append('div')
      .attr('class', 'network-tooltip')
      .style('position', 'absolute')
      .style('opacity', 0)
      .style('background', 'white')
      .style('border', '1px solid #e5e7eb')
      .style('border-radius', '6px')
      .style('padding', '8px 12px')
      .style('pointer-events', 'none')
      .style('box-shadow', '0 4px 6px rgba(0, 0, 0, 0.1)')
      .style('font-size', '14px')
      .style('z-index', '1000');

    // 更新位置
    simulation.on('tick', () => {
      link
        .attr('x1', (d) => d.source.x)
        .attr('y1', (d) => d.source.y)
        .attr('x2', (d) => d.target.x)
        .attr('y2', (d) => d.target.y);

      node.attr('cx', (d) => d.x).attr('cy', (d) => d.y);

      label.attr('x', (d) => d.x).attr('y', (d) => d.y);
    });

    // 拖拽函數
    function dragStarted(event) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    }

    function dragged(event) {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    }

    function dragEnded(event) {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    }

    // 清理函數
    return () => {
      simulation.stop();
      tooltip.remove();
    };
  }, [data, onNodeClick]);

  return (
    <div ref={containerRef} className="w-full">
      {data && data.nodes && data.nodes.length > 0 ? (
        <>
          <svg ref={svgRef} className="border border-gray-200 rounded-lg"></svg>
          <div className="mt-4 flex items-center justify-center space-x-6 text-sm text-gray-600">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 rounded-full bg-blue-500"></div>
              <span>一般作者</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 rounded-full bg-yellow-500"></div>
              <span>關鍵人物</span>
            </div>
            <div className="flex items-center space-x-2">
              <span>節點大小 = 論文數量</span>
            </div>
            <div className="flex items-center space-x-2">
              <span>連線粗細 = 合作次數</span>
            </div>
          </div>
        </>
      ) : (
        <div className="flex items-center justify-center h-96 text-gray-500">
          無網絡數據
        </div>
      )}
    </div>
  );
}
