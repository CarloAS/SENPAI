function plot_swc(swcFile)
    % Read SWC file
    swc = readtable(swcFile,"FileType","text","Delimiter",' ');
    
    % Extract coordinates and other columns
    x = swc{:, 3};  % Extract data from column 3 (x coordinates)
    y = swc{:, 4};  % Extract data from column 4 (y coordinates)
    z = swc{:, 5};  % Extract data from column 5 (z coordinates)
    r = swc{:, 6};  % Extract data from column 6 (radius)
    parent = swc{:, 7};  % Extract data from column 7 (parent index)
    
    % Convert to double if needed (it's typically already double)
    x = double(x);
    y = double(y);
    z = double(z);
    r = double(r);
    parent = double(parent);
    
    % Plot
    figure;
    hold on;
    % Plot nodes
    scatter3(x, y, z, 'filled');
    % Plot connections
    for i = 1:length(parent)
        if parent(i) ~= -1  % If not root
            plot3([x(i) x(parent(i))], ...
                  [y(i) y(parent(i))], ...
                  [z(i) z(parent(i))], 'b-');
        end
    end
    axis equal;
    grid on;
    xlabel('X'); ylabel('Y'); zlabel('Z');
    title('Neuron Morphology');
end