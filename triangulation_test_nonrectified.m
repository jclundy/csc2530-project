close all;
clear all;

alpha = 80 * pi / 180;
u_actual = 1251;
v_actual = 541;
Z_w_actual_1 = 117;
Z_w_actual_2 = 124.5;

% laserDotLocation_pixels
u_val = 715;
v_val = 485;
%%
M= [[1.43864737e+03 0.00000000e+00 1.01778586e+03];
 [0.00000000e+00 1.43225687e+03 5.79732557e+02];
 [0.00000000e+00 0.00000000e+00 1.00000000e+00]];

dist= [-0.44544757  0.26793777 -0.01078108 -0.01066561 -0.10889512];

k1 = dist(1);
k2 = dist(2);
p1 = dist(3);
p2 = dist(4);
k3 = dist(5);
k4 = 0;
k5 = 0;
k6 = 0;
s1 = 0;
s2 = 0;
s3 = 0;
s4 = 0;
taux = 0;
tauy = 0;

syms theta real;

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

T = [tx; ty; tz]
theta_x = 0;
theta_y = 0;
theta_z = pi; % 180 deg - camera is flipped over

z_tilt = 4 * pi/ 180; % 4 degree tilt

R = Rz_fun(theta_z + z_tilt);

Rt = [R, T]

%%
M_Rt = M * Rt



%%
img_h = 1080;
img_w = 1920;

gamma = 0;
N = 550; %distMax
distMin = 16;

u_vals = zeros(1,N);
v_vals = zeros(1,N);

P_w_vals = zeros(3,N);
P_c_vals = zeros(3,N);


r_c = zeros(1,N);

for i=distMin:N
    Z_w = i;
    X_w = -Z_w * tan(pi/2 - alpha);
    Y_w = -Z_w * tan(gamma);

    P_w = [X_w; Y_w; Z_w; 1];

    P_c = Rt * P_w;
    X_c = P_c(1);
    Y_c = P_c(2);
    Z_c = P_c(3);

    x_prime = X_c / Z_c;
    y_prime = Y_c / Z_c;

    r = sqrt(x_prime^2 + y_prime^2);

    x_pprime = x_prime * (1+k1*r^2 + k2 *r^4 + k3 * r^6) + 2 * p1 * x_prime * y_prime + p2 * (r^2 +2*x_prime^2);
    y_pprime = y_prime * (1+k1*r^2 + k2 *r^4 + k3 * r^6) + p1 * (r^2+2*y_prime^2)+ 2*p2* x_prime * y_prime;

    fx = M(1,1);
    fy = M(2,2);
    cx = M(1,3);
    cy = M(2,3);

    u = fx * x_pprime + cx;
    v = fy * y_pprime + cy;

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

figure()
plot(Z_w_vals, [u_vals; v_vals])
title("Zw vs u, v")
legend("u", "v")
yline(0);
yline(img_w);

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

u_indices = find(u_vals > 0)

u_vals_fitting = u_vals(u_indices);
Z_w_vals_fitting = Z_w_vals(u_indices);

x_max = max(u_vals)

x = (0:1:x_max);

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
xlabel("u value")
ylabel("Z")

%%

% Zw_predicted = ppval(pp, u_actual)
% 
% pp_inverse = spline(Z_w_vals_fitting', u_vals_fitting');
% 
% u_predicted1 = ppval(pp_inverse, Z_w_actual_1)
% u_predicted2 = ppval(pp_inverse, Z_w_actual_2)

u_actual_vals = [1026, 1116, 1120, 1175, 1189];
Zw_predicted_vals = ppval(pp, u_actual_vals)'

