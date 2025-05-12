function  [spher_marks] = senpai_somamark( Img, initMarks, disprange, initS)
% SENPAI_SOMAMARK is a GUI that allows to mark somas or sinks for the
% catchment basins required by the SENPAI toolbox.
% Usage:
%  senpai_somamark ( Image )
%  senpai_somamark ( Image , initMarks )
%  senpai_somamark ( Image , initMarks, disprange )
%  senpai_somamark ( Image , initMarks, disprange, initS )
% 
%    Image:      3D image MxNxKxC (K slices of MxN images) C is either 1
%                (for grayscale images) or 3 (for RGB images) 
%    InitMarks:  3D image MxNxK (K slices of MxN images), a binary mask of 
%                already-segmented somas, new somas will be appended 
%    disprange:  see [LOW HIGH] inputs to imshow3D below
%    initS:      slice to display at the start of the gui.
%
% This function is based on imshow3D:
% IMSHOW3D displays 3D grayscale or RGB images in a slice by slice fashion
%with mouse-based slice browsing and window and level adjustment control,
%and auto slice browsing control.
%
% Usage:
% imshow3D ( Image )
% imshow3D ( Image , [] )
% imshow3D ( Image , [LOW HIGH] )
% imshow3D ( Image , [] , initsn )
%   
%    Image:      3D image MxNxKxC (K slices of MxN images) C is either 1
%                (for grayscale images) or 3 (for RGB images)  
%    [LOW HIGH]: display range that controls the display intensity range of
%                a grayscale image (default: the broadest available range)
%    initsn:     The slice number to be displayed initially (default:
%                mid-slice number) 
%
% Use the scroll bar or mouse scroll wheel to switch between slices. To
% adjust window and level values keep the mouse right button pressed, and
% drag the mouse up and down (for level adjustment) or right and left (for
% window adjustment). Window and level adjustment control works only for
% grayscale images.
% "Play" button displays all the slices as a sequence of frames. The time
% interval value can also be adjusted (default time interval is 100 ms).
% 
% "Auto W/L" button adjust the window and level automatically for grayscale
% images.
%
% While "Fine Tune" checkbox is checked the window/level adjustment gets 16
% times less sensitive to mouse movement, to make it easier to control
% display intensity rang.
%
% Note: The sensitivity of mouse-based window and level adjustment is set
% based on the user-defined display intensity range; the wider the range,
% the more sensitivity to mouse drag.
% 
% Note: IMSHOW3DFULL is a newer version of IMSHOW3D (also available on
% MathWorks) that displays 3D grayscale or RGB images from three
% perpendicular views (i.e., axial, sagittal, and coronal).
% 
%   Example
%   --------
%       % To display an image (MRI example)
%       load mri 
%       Image = squeeze(D); 
%       figure, 
%       imshow3D(Image) 
%
%       % To display the image, and adjust the display range
%       figure,
%       imshow3D(Image,[20 100]);
%
%       % To define the initial slice number
%       figure,
%       imshow3D(Image,[],5);
%
%   See also IMSHOW.

%
% - Maysam Shahedi (mshahedi@gmail.com)
% - Released: 1.0.0   Date: 2013/04/15
% - Revision: 1.1.0   Date: 2013/04/19
% - Revision: 1.5.0   Date: 2016/09/22
% - Revision: 1.6.0   Date: 2018/06/07
% - Revision: 1.6.1   Date: 2018/10/29
% 

sno = size(Img,3);  % number of slices
S = round(sno/2);

PlayFlag = false;   % Play flag, playing when it is 'True'
Tinterv = 100;

global InitialCoord;

MinV = 0;
MaxV = max(Img(:));
LevV = (double( MaxV) + double(MinV)) / 2;
Win = double(MaxV) - double(MinV);
WLAdjCoe = (Win + 1)/1024;
FineTuneC = [1 1/16];    % Regular/Fine-tune mode coefficients
[xmg, ymg, zmg]=meshgrid(1:size(Img,2),1:size(Img,1),1:size(Img,3));
rad_sph=40;
z_fact=3;

if isa(Img,'uint8')
    MaxV = uint8(Inf);
    MinV = uint8(-Inf);
    LevV = (double( MaxV) + double(MinV)) / 2;
    Win = double(MaxV) - double(MinV);
    WLAdjCoe = (Win + 1)/1024;
elseif isa(Img,'uint16')
    MaxV = uint16(Inf);
    MinV = uint16(-Inf);
    LevV = (double( MaxV) + double(MinV)) / 2;
    Win = double(MaxV) - double(MinV);
    WLAdjCoe = (Win + 1)/1024;
elseif isa(Img,'uint32')
    MaxV = uint32(Inf);
    MinV = uint32(-Inf);
    LevV = (double( MaxV) + double(MinV)) / 2;
    Win = double(MaxV) - double(MinV);
    WLAdjCoe = (Win + 1)/1024;
elseif isa(Img,'uint64')
    MaxV = uint64(Inf);
    MinV = uint64(-Inf);
    LevV = (double( MaxV) + double(MinV)) / 2;
    Win = double(MaxV) - double(MinV);
    WLAdjCoe = (Win + 1)/1024;
elseif isa(Img,'int8')
    MaxV = int8(Inf);
    MinV = int8(-Inf);
    LevV = (double( MaxV) + double(MinV)) / 2;
    Win = double(MaxV) - double(MinV);
    WLAdjCoe = (Win + 1)/1024;
elseif isa(Img,'int16')
    MaxV = int16(Inf);
    MinV = int16(-Inf);
    LevV = (double( MaxV) + double(MinV)) / 2;
    Win = double(MaxV) - double(MinV);
    WLAdjCoe = (Win + 1)/1024;
elseif isa(Img,'int32')
    MaxV = int32(Inf);
    MinV = int32(-Inf);
    LevV = (double( MaxV) + double(MinV)) / 2;
    Win = double(MaxV) - double(MinV);
    WLAdjCoe = (Win + 1)/1024;
elseif isa(Img,'int64')
    MaxV = int64(Inf);
    MinV = int64(-Inf);
    LevV = (double( MaxV) + double(MinV)) / 2;
    Win = double(MaxV) - double(MinV);
    WLAdjCoe = (Win + 1)/1024;
elseif isa(Img,'logical')
    MaxV = 0;
    MinV = 1;
    LevV =0.5;
    Win = 1;
    WLAdjCoe = 0.1;
end    

SFntSz = 9;
txtFntSz = 10;
LVFntSz = 9;
WVFntSz = 9;
BtnSz = 10;

if (nargin < 4)
    S = round(sno/2);
else
    S = initS;
    if S > sno
        S = sno;
        warning('Initial slice number out of range');
    elseif S < 1
        S = 1;
        warning('Initial slice number out of range');
    end
end

if (nargin < 3)
    [Rmin Rmax] = WL2R(Win, LevV);
elseif numel(disprange) == 0
    [Rmin Rmax] = WL2R(Win, LevV);
else
    LevV = (double(disprange(2)) + double(disprange(1))) / 2;
    Win = double(disprange(2)) - double(disprange(1));
    WLAdjCoe = (Win + 1)/1024;
    [Rmin Rmax] = WL2R(Win, LevV);
end

spher_marks = zeros(size(Img),'like',Img);
if nargin > 1
    spher_marks(initMarks>0)=max(Img(:));
end

clf

%axes('position',[0,0.2,1,0.8]), imshow(toplot, [Rmin Rmax])
axes('position',[0,0.2,1,0.8]), imshow(imfuse(squeeze(Img(:,:,S,:)),spher_marks(:,:,S)>0,'falsecolor'), [Rmin Rmax])

FigPos = get(gcf,'Position');
S_Pos = [30 45 uint16(FigPos(3)-100)+1 20];
Stxt_Pos = [30 65 uint16(FigPos(3)-100)+1 15];
Wtxt_Pos = [20 18 60 20];
Wval_Pos = [75 20 50 20];
Ltxt_Pos = [130 18 45 20];
Lval_Pos = [170 20 50 20];
Btn_Pos = [240 20 70 20];
ChBx_Pos = [320 20 80 20];
Play_Pos = [uint16(FigPos(3)-100)+40 45 30 20];
Time_Pos = [uint16(FigPos(3)-100)+35 20 40 20];
Ttxt_Pos = [uint16(FigPos(3)-100)-50 18 90 20];
mark_Btn_Pos = [420 20 140 20];
Rad_Pos = [580 20 50 20];
Zad_Pos = [700 20 50 20];
Undo_Pos = [800 20 50 20];

% W/L Button styles:
WL_BG = ones(Btn_Pos(4),Btn_Pos(3),3)*0.85;
WL_BG(1,:,:) = 1; WL_BG(:,1,:) = 1; WL_BG(:,end-1,:) = 0.6; WL_BG(:,end,:) = 0.4; WL_BG(end,:,:) = 0.4;

% Play Button styles:
Play_BG = ones(Play_Pos(4),Play_Pos(3),3)*0.85;
Play_BG(1,:,:) = 1; Play_BG(:,1,:) = 1; Play_BG(:,end-1,:) = 0.6; Play_BG(:,end,:) = 0.4; Play_BG(end,:,:) = 0.4;
Play_Symb = [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1;...
             0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1; 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1; 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1;...
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0; 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1; 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1;...
             0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1; 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1; 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1;...
             0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1];
Play_BG(floor((Play_Pos(4)-13)/2)+1:floor((Play_Pos(4)-13)/2)+13,floor(Play_Pos(3)/2)-7:floor(Play_Pos(3)/2)+6,:) = ...
    repmat(Play_Symb,1,1,3) .* Play_BG(floor((Play_Pos(4)-13)/2)+1:floor((Play_Pos(4)-13)/2)+13,floor(Play_Pos(3)/2)-7:floor(Play_Pos(3)/2)+6,:);
Pause_BG = ones(Play_Pos(4),Play_Pos(3),3)*0.85;
Pause_BG(1,:,:) = 1; Pause_BG(:,1,:) = 1; Pause_BG(:,end-1,:) = 0.6; Pause_BG(:,end,:) = 0.4; Pause_BG(end,:,:) = 0.4;
Pause_Symb = repmat([0, 0, 0, 1, 1, 1, 1, 0, 0, 0],13,1);
Pause_BG(floor((Play_Pos(4)-13)/2)+1:floor((Play_Pos(4)-13)/2)+13,floor(Play_Pos(3)/2)-5:floor(Play_Pos(3)/2)+4,:) = ...
    repmat(Pause_Symb,1,1,3) .* Pause_BG(floor((Play_Pos(4)-13)/2)+1:floor((Play_Pos(4)-13)/2)+13,floor(Play_Pos(3)/2)-5:floor(Play_Pos(3)/2)+4,:);


if sno > 1
    shand = uicontrol('Style', 'slider','Min',1,'Max',sno,'Value',S,'SliderStep',[1/(sno-1) 10/(sno-1)],'Position', S_Pos,'Callback', {@SliceSlider, Img});
    stxthand = uicontrol('Style', 'text','Position', Stxt_Pos,'String',sprintf('Slice# %d / %d',S, sno), 'FontSize', SFntSz);
    playhand = uicontrol('Style', 'pushbutton','Position', Play_Pos, 'Callback' , @Play);
    set(playhand, 'cdata', Play_BG)
    ttxthand = uicontrol('Style', 'text','Position', Ttxt_Pos,'String','Interval (ms): ',  'FontSize', txtFntSz);
    timehand = uicontrol('Style', 'edit','Position', Time_Pos,'String',sprintf('%d',Tinterv), 'BackgroundColor', [1 1 1], 'FontSize', LVFntSz,'Callback', @TimeChanged);
else
    stxthand = uicontrol('Style', 'text','Position', Stxt_Pos,'String','2D image', 'FontSize', SFntSz);
end    
ltxthand = uicontrol('Style', 'text','Position', Ltxt_Pos,'String','Level: ',  'FontSize', txtFntSz);
wtxthand = uicontrol('Style', 'text','Position', Wtxt_Pos,'String','Window: ',  'FontSize', txtFntSz);
lvalhand = uicontrol('Style', 'edit','Position', Lval_Pos,'String',sprintf('%6.0f',LevV), 'BackgroundColor', [1 1 1], 'FontSize', LVFntSz,'Callback', @WinLevChanged);
wvalhand = uicontrol('Style', 'edit','Position', Wval_Pos,'String',sprintf('%6.0f',Win), 'BackgroundColor', [1 1 1], 'FontSize', WVFntSz,'Callback', @WinLevChanged);
Btnhand = uicontrol('Style', 'pushbutton','Position', Btn_Pos,'String','Auto W/L', 'FontSize', BtnSz, 'Callback' , @AutoAdjust);
set(Btnhand, 'cdata', WL_BG)
%SC!
BtnRad = uicontrol('Style', 'pushbutton','Position', mark_Btn_Pos,'String','Mark with radius:', 'FontSize', BtnSz, 'Callback' , @markSoma);
%set(BtnRad, 'cdata', WL_BG)
radhand = uicontrol('Style', 'edit','Position', Rad_Pos,'String',sprintf('%6.0f',rad_sph), 'BackgroundColor', [1 1 1], 'FontSize', WVFntSz,'Callback', @RadLevChanged);
zhand = uicontrol('Style', 'edit','Position', Zad_Pos,'String',sprintf('%6.0f',z_fact), 'BackgroundColor', [1 1 1], 'FontSize', WVFntSz,'Callback', @ZfactChanged);
BtnUndo = uicontrol('Style', 'pushbutton','Position', Undo_Pos,'String','Undo', 'FontSize', BtnSz, 'Callback' , @markUndo);
ztxthand = uicontrol('Style', 'text','Position', [650 20 50 20],'String','z-fact: ',  'FontSize', txtFntSz);
xydt=[1 1];
zdt=1;

ChBxhand = uicontrol('Style', 'checkbox','Position', ChBx_Pos,'String','Fine-tune', 'FontSize', txtFntSz);

set (gcf, 'WindowScrollWheelFcn', @mouseScroll);
set (gcf, 'ButtonDownFcn', @mouseClick);
set(get(gca,'Children'),'ButtonDownFcn', @mouseClick);
set(gcf,'WindowButtonUpFcn', @mouseRelease);
set(gcf,'ResizeFcn', @figureResized);


% -=< Figure resize callback function >=-
    function figureResized(object, eventdata)
        FigPos = get(gcf,'Position');
        S_Pos = [30 45 uint16(FigPos(3)-100)+1 20];
        Stxt_Pos = [30 65 uint16(FigPos(3)-100)+1 15];
        Play_Pos = [uint16(FigPos(3)-100)+40 45 30 20];
        Time_Pos = [uint16(FigPos(3)-100)+35 20 40 20];
        Ttxt_Pos = [uint16(FigPos(3)-100)-50 18 90 20];
        if sno > 1
            set(shand,'Position', S_Pos);
            set(playhand, 'Position', Play_Pos)
            set(ttxthand, 'Position', Ttxt_Pos)
            set(timehand, 'Position', Time_Pos)
        end
        set(stxthand,'Position', Stxt_Pos);
        set(ltxthand,'Position', Ltxt_Pos);
        set(wtxthand,'Position', Wtxt_Pos);
        set(lvalhand,'Position', Lval_Pos);
        set(wvalhand,'Position', Wval_Pos);
        set(Btnhand,'Position', Btn_Pos);
        set(ChBxhand,'Position', ChBx_Pos);
    end

% -=< Slice slider callback function >=-
    function SliceSlider (hObj,event, Img)
        S = round(get(hObj,'Value'));
        toplot=squeeze(Img(:,:,S,:));toplot(spher_marks(:,:,S)>0)=max(Img(:));
        set(get(gca,'children'),'cdata',imfuse(squeeze(Img(:,:,S,:)),spher_marks(:,:,S)>0,'falsecolor'))
        caxis([Rmin Rmax])
        if sno > 1
            set(stxthand, 'String', sprintf('Slice# %d / %d',S, sno));
        else
            set(stxthand, 'String', '2D image');
        end
    end


% SC!
% -=< marker callback function >=-
    function markSoma (hObj,event, Img)
        d=datacursormode(gcf);
        xydt=getCursorInfo(d).Position;
        zdt=S;
        spher_marks( (xmg-xydt(1)).^2 + (ymg-xydt(2)).^2 + ((zmg-zdt).*z_fact).^2 <= rad_sph^2)=1;
        assignin('base','spher_marks',spher_marks);
        %Img(spher_marks)=max(Img(:));
    end
    function ZfactChanged(varargin)
        z_fact = str2double(get(zhand, 'string'));
        if (z_fact < 1)
            z_fact = 1;
        end
    end
% -=< radius level text adjustment >=-
    function RadLevChanged(varargin)
        rad_sph = str2double(get(radhand, 'string'));
        if (rad_sph < 1)
            rad_sph = 1;
        end
    end
    function markUndo (hObj,event, Img)
        spher_marks( (xmg-xydt(1)).^2 + (ymg-xydt(2)).^2 + ((zmg-zdt).*z_fact).^2 <= rad_sph^2)=0;
        assignin('base','spher_marks',spher_marks);
        %Img(spher_marks)=max(Img(:));
    end

% -=< Mouse scroll wheel callback function >=-
    function mouseScroll (object, eventdata)
        UPDN = eventdata.VerticalScrollCount;
        S = S - UPDN;
        if (S < 1)
            S = 1;
        elseif (S > sno)
            S = sno;
        end
        if sno > 1
            set(shand,'Value',S);
            set(stxthand, 'String', sprintf('Slice# %d / %d',S, sno));
        else
            set(stxthand, 'String', '2D image');
        end
        toplot=squeeze(Img(:,:,S,:));toplot(spher_marks(:,:,S)>0)=max(Img(:));
        set(get(gca,'children'),'cdata',imfuse(squeeze(Img(:,:,S,:)),spher_marks(:,:,S)>0,'falsecolor'))
    end

% -=< Mouse button released callback function >=-
    function mouseRelease (object,eventdata)
        set(gcf, 'WindowButtonMotionFcn', '')
    end

% -=< Mouse click callback function >=-
    function mouseClick (object, eventdata)
        MouseStat = get(gcbf, 'SelectionType');
        if (MouseStat(1) == 'a')        %   RIGHT CLICK
            InitialCoord = get(0,'PointerLocation');
            set(gcf, 'WindowButtonMotionFcn', @WinLevAdj);
        end
    end

% -=< Window and level mouse adjustment >=-
    function WinLevAdj(varargin)
        PosDiff = get(0,'PointerLocation') - InitialCoord;

        Win = Win + PosDiff(1) * WLAdjCoe * FineTuneC(get(ChBxhand,'Value')+1);
        LevV = LevV - PosDiff(2) * WLAdjCoe * FineTuneC(get(ChBxhand,'Value')+1);
        if (Win < 1)
            Win = 1;
        end

        [Rmin, Rmax] = WL2R(Win,LevV);
        caxis([Rmin, Rmax])
        set(lvalhand, 'String', sprintf('%6.0f',LevV));
        set(wvalhand, 'String', sprintf('%6.0f',Win));
        InitialCoord = get(0,'PointerLocation');
    end

% -=< Window and level text adjustment >=-
    function WinLevChanged(varargin)

        LevV = str2double(get(lvalhand, 'string'));
        Win = str2double(get(wvalhand, 'string'));
        if (Win < 1)
            Win = 1;
        end

        [Rmin, Rmax] = WL2R(Win,LevV);
        caxis([Rmin, Rmax])
    end

% -=< Window and level to range conversion >=-
    function [Rmn Rmx] = WL2R(W,L)
        Rmn = L - (W/2);
        Rmx = L + (W/2);
        if (Rmn >= Rmx)
            Rmx = Rmn + 1;
        end
    end

% -=< Window and level auto adjustment callback function >=-
    function AutoAdjust(object,eventdata)
        Win = double(max(Img(:))-min(Img(:)));
        Win (Win < 1) = 1;
        LevV = double(min(Img(:)) + (Win/2));
        [Rmin, Rmax] = WL2R(Win,LevV);
        caxis([Rmin, Rmax])
        set(lvalhand, 'String', sprintf('%6.0f',LevV));
        set(wvalhand, 'String', sprintf('%6.0f',Win));
    end

% -=< Play button callback function >=-
    function Play (hObj,event)
        PlayFlag = ~PlayFlag;
        if PlayFlag
            set(playhand, 'cdata', Pause_BG)
        else
            set(playhand, 'cdata', Play_BG)
        end            
        while PlayFlag
            S = S + 1;
            if (S > sno)
                S = 1;
            end
            set(shand,'Value',S);
            set(stxthand, 'String', sprintf('Slice# %d / %d',S, sno));
            toplot=squeeze(Img(:,:,S,:));toplot(spher_marks(:,:,S)>0)=max(Img(:));
            set(get(gca,'children'),'cdata',imfuse(squeeze(Img(:,:,S,:)),spher_marks(:,:,S)>0,'falsecolor'))
            pause(Tinterv/1000)
        end
    end

% -=< Time interval adjustment callback function>=-
    function TimeChanged(varargin)
        Tinterv = str2double(get(timehand, 'string'));
    end
    
end
% -=< Maysam Shahedi (mshahedi@gmail.com), October 29, 2018>=-