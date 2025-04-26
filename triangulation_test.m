close all;
clear all;

alpha = 80 * pi / 180;
u_actual = 1251;
v_actual = 541;
Z_w_actual_1 = 117;
Z_w_actual_2 = 124.5;
%%


uv_vals = [[ 400.  660.];
 [ 653.  618.];
 [ 842.  585.];
 [ 931.  569.];
 [ 987.  559.];
 [1023.  552.];
 [1047.  547.]];

u_actual_vals = uv_vals(:,1);
v_actual_vals = uv_vals(:,2);


%%
camera_distance_to_wall_vals = [16.6 25.9 40.9 55.5 71.1 86.4 100.9];
camera_distance_to_laser_dot = [23.5 29.7 42.9 56.6 71.7 86.3 101];

%%
M = [[8.66684224e+02, 0.00000000e+00, 1.02183430e+03];
        [0.00000000e+00, 8.71185415e+02, 5.37725759e+02];
        [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]];


% laserDotLocation_pixels
u_val = 715;
v_val = 485;

syms s theta real;


Rz_sym = [cos(theta), -sin(theta), 0; sin(theta), cos(theta), 0; 0, 0, 1];
Rx_sym = [1, 0,0; 0, cos(theta), -sin(theta); 0, sin(theta), cos(theta)];
Ry_sym = [cos(theta), 0, sin(theta); 0, 1,0; -sin(theta), 0, cos(theta)];

Rx_fun = matlabFunction(Rx_sym, 'Vars', {theta});
Ry_fun = matlabFunction(Ry_sym, 'Vars', {theta});
Rz_fun = matlabFunction(Rz_sym, 'Vars', {theta});

%%
tx = -19.2; %cm
ty = -5.5; %cm
tz = 2; %cm

T = [tx; ty; tz];
theta_x = 20 * pi/180;
theta_y = 20 * pi/180;
theta_z = pi; % 180 deg - camera is flipped over

z_tilt = 4 * pi/ 180; % 4 degree tilt

Ry = Rz_fun(theta_y);
Rx = Rx_fun(theta_x);
R = Rx*Ry*Rz_fun(theta_z + z_tilt);

Rt = [R, T];

%%
M_Rt = M * Rt;


syms t_gamma Zw s

Xw = -Zw / tan(alpha);
Yw = t_gamma*Zw;

Pw = [Xw; Yw; Zw; 1];

M_Rt * Pw / s;

% x = fsolve()

syms x1 x2 x3 real

syms u v real

% x1 = s
% x2 = tan(gamma)*Zw
% x3 = Zw

eqn_sym = [u;v;1]*s - M * Rt * Pw;

eqn = subs(eqn_sym, u, u_val);
eqn = subs(eqn, v, v_val);


X = [s; Zw; t_gamma];

eqn_fun = matlabFunction(eqn, 'Vars', {X})
%%
x0 = [1; 209; 0];
options = optimoptions('fsolve','Display','off');
[x,fval,exitflag,output] = fsolve(eqn_fun,x0,options);

%%
eqn1 = subs(eqn, t_gamma, 0);
x0_1 = [1; 1]
eqn1_fun = matlabFunction(eqn1, 'Vars', {[s; Zw]})
options = optimoptions('fsolve','Display','off');
[x,fval,exitflag,output] = fsolve(eqn1_fun,x0_1,options);

%%
% eqn2 =  [715*s - 706.4351*Zw + 15.1257*Zw*t_gamma + 1.4597e+04; 
%         485*s - 532.1919*Zw - 871.0527*Zw*t_gamma + 3.7161e+03;
%                                             s - Zw - 2]
% x1 - s
% x2 - Zw
% x3 - Zw*tan(gamma)
eqn2 =  [715*x1 - 706.4351*x2 + 15.1257*x3 + 1.4597e+04; 
        485*x1 - 532.1919*x2 - 871.0527*x3+ 3.7161e+03;
                                            x1 - x2 - 2];
eqn2_fun = matlabFunction(eqn2, 'Vars', {[x1; x2; x3]});

x0_2 = [0;0;0];

options = optimoptions('fsolve','Display','off');
[x,fval,exitflag,output] = fsolve(eqn2_fun,x0_2,options);

s_val = x(1);
Zw_val = x(2);
t_gamma_val = x(3) / Zw_val;
gamma = atan(t_gamma_val);
%%
img_h = 1080;
img_w = 1920;

gamma = 0;
N = 500;

u_vals = zeros(1,N);
v_vals = zeros(1,N);

P_w_vals = zeros(3,N);
P_c_vals = zeros(3,N);


r_c = zeros(1,N);

for i=1:N
    Z_w = i;
    X_w = -Z_w * tan(pi/2 - alpha);
    Y_w = -Z_w * tan(gamma);

    P_w = [X_w; Y_w; Z_w; 1];

    P_c = Rt * P_w;
    X_c = P_c(1);
    Y_c = P_c(2);
    Z_c = P_c(3);

    fx = M(1,1);
    fy = M(2,2);
    cx = M(1,3);
    cy = M(2,3);

    u = fx * X_c / Z_c + cx;
    v = fy * Y_c / Z_c + cy;

    u_vals(i) = u;
    v_vals(i) = v;

    P_w_vals(:,i) = P_w(1:3);
    P_c_vals(:,i) = P_c;


end

Z_w_vals = P_w_vals(3,:);
X_w_vals = P_w_vals(1,:);
X_c_vals = P_c_vals(1,:);

figure()
plot(Z_w_vals, X_w_vals)
title("Zw vs Xw")
%%
figure()
r_vals = sqrt(u_vals.^2 + v_vals.^2);
plot(Z_w_vals, [u_vals; v_vals; r_vals])
hold on;
plot(camera_distance_to_wall_vals', u_actual_vals, "o");
plot(camera_distance_to_laser_dot', u_actual_vals, "+");

plot(camera_distance_to_wall_vals', v_actual_vals, "o");
plot(camera_distance_to_laser_dot', v_actual_vals, "o");

hold off;
title("Zw vs u, v")
legend("u", "v", "r", "u actual - dist to wall", "u actual - dist to dot", "v -dist to wall", "v - dist to dot")
yline(0);
yline(img_w);
%%
figure()
plot(Z_w_vals, P_c_vals)
title("Zw vs Xc, Yc, Zc")
legend("Xc", "Yc", "Zc")

% Inverse mapping:
figure()

plot(u_vals, Z_w_vals, "Marker", ".")
title("inverse map")
xline(0);
xline(img_w);

%% curve fitting

u_indices = find(u_vals > 0);

u_vals_fitting = u_vals(u_indices);
v_vals_fitting = v_vals(u_indices);

r_vals_fitting = u_vals_fitting.^2 + v_vals_fitting.^2;
r_vals_fitting = sqrt(r_vals_fitting);

Z_w_vals_fitting = Z_w_vals(u_indices);

x_min = min(u_vals_fitting);
x_max = max(u_vals_fitting);

x = (x_min:1:x_max);

% f = fit(u_vals_fitting', Z_w_vals_fitting', 'exp1')

pp = spline(u_vals_fitting', Z_w_vals_fitting');
spline_vals = ppval(pp, x);
figure()
plot(x, spline_vals)
title("spline vals")

figure()
plot(x, spline_vals)
hold on;
plot(u_vals_fitting, Z_w_vals_fitting)
hold off;
legend("curve fit", "calculated")

pp_r = spline(r_vals_fitting', Z_w_vals_fitting');

r_vals_min = min(r_vals_fitting);
r_vals_max = max(r_vals_fitting);
r_vals_plot = (r_vals_min:1:r_vals_max);
spline_vals_r = ppval(pp, r_vals_plot);

figure()
plot(r_vals_plot, spline_vals_r)
title("spline vals r")

%%

% Zw_predicted = ppval(pp, u_actual)
% 
% pp_inverse = spline(Z_w_vals_fitting', u_vals_fitting');
% 
% u_predicted1 = ppval(pp_inverse, Z_w_actual_1)
% u_predicted2 = ppval(pp_inverse, Z_w_actual_2)

% u_actual_vals = [1082, 1116, 1120, 1175, 1189];


% 1082, 1116, 1120, 1175, 1189
Zw_predicted_vals = ppval(pp, u_actual_vals);

figure()
plot(u_actual_vals, [camera_distance_to_wall_vals', camera_distance_to_laser_dot', Zw_predicted_vals])
legend("camera to wall", "camera to dot", "Zw predicted")

%%
pp_calib = spline(u_actual_vals', camera_distance_to_wall_vals');
Zw_predicted_vals_calibration = ppval(pp_calib, u_vals_fitting);
figure()
plot(u_vals_fitting, Zw_predicted_vals_calibration)
hold on;
plot(u_actual_vals, camera_distance_to_wall_vals', "Marker", "o");
hold off;
%% predicted values from sqrt(u,v)


%% predicted values from other tests:
far_test_u_vals = [1082 1116 1120 1175 1189];
actual_far_distances = [117 209 207.5 384 493.5];
Zw_predicted_vals_calibration_far = ppval(pp_calib, far_test_u_vals);
figure()
plot(far_test_u_vals, Zw_predicted_vals_calibration_far)
hold on;
plot(far_test_u_vals, actual_far_distances', "Marker", "o");
legend("predicted", "actual")


%% Poly fit test 1

degree = 4;
polyfit_calib = polyfit(u_actual_vals', camera_distance_to_wall_vals', degree);
Zw_predicted_vals_calibration = polyval(polyfit_calib, u_vals_fitting);
figure()
plot(u_vals_fitting, Zw_predicted_vals_calibration)
hold on;
plot(u_actual_vals, camera_distance_to_wall_vals', "Marker", "o");
hold off;
title("poly fit")

%% Mesh view
figure()
scatter3(u_actual_vals,v_actual_vals, camera_distance_to_wall_vals);
xlabel('x'); ylabel('y');
title("Spline")