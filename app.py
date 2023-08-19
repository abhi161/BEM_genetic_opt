import aerosandbox as asb
import numpy as np


# Define the propeller geometry
diameter = 0.2286  # meters
n_blades = 2
r_hub = 0.0127  # meters
r_tip = diameter / 2
n_sections = 20
r = np.linspace(r_hub, r_tip, n_sections)
chord = np.array([0.028, 0.031, 0.035, 0.038, 0.04, 0.042, 0.043, 0.044, 0.044, 0.043, 0.041,
                  0.039, 0.036, 0.032, 0.027, 0.02, 0.012, 0.005, 0.0, 0.0])  # meters
twist = np.deg2rad(np.array([-25.0, -24.0, -23.0, -22.0, -21.0, -20.0, -19.0, -18.0, -17.0, -16.0,
                             -15.0, -14.0, -13.0, -12.0, -11.0, -10.0, -9.0, -8.0, -7.0, -6.0]))  # radians
theta = np.linspace(0, 2 * np.pi, 50)

# Define the operating conditions
RPM = 10000
V_inf = 0  # freestream velocity, m/s
rho = 1.225  # air density, kg/m^3
temperature = 300  # K

# Define the airfoil
airfoil = asb.Airfoil("naca0012")

# Calculate the angle of attack and Reynolds number at each section of the blade
alpha = np.zeros((n_sections, len(theta)))
Re = np.zeros((n_sections, len(theta)))
for i in range(n_sections):
    for j in range(len(theta)):
        V = np.sqrt(V_inf ** 2 + asb.tangential_induction_factor(0, RPM, rho, V_inf, diameter, r[i], n_blades) ** 2)
        alpha[i, j] = asb.degrees(
            np.arctan(
                asb.axial_induction_factor(0, RPM, rho, V_inf, diameter, r[i], chord[i], twist[i], n_blades, asb.viscosity_air(temperature), asb.reynolds_number(V, chord[i], temperature, rho, asb.length_reference), airfoil) /
                asb.tangential_induction_factor(0, RPM, rho, V_inf, diameter, r[i], n_blades)
            )
        )
        Re[i, j] = asb.reynolds_number(V, chord[i], temperature, rho, asb.length_reference)

# Calculate the aerodynamic forces and moments
forces = asb.zeros((n_sections, len(theta), 3))
moments = asb.zeros((n_sections, len(theta), 3))
for i in range(n_sections):
    for j in range(len(theta)):
        element = asb.BladeElement(
            r=r[i],
            chord=chord[i],
            twist=twist[i],
            airfoil=airfoil,
            alpha=alpha[i, j],
            Re=Re[i, j]
        )
        element.set_condition(
                V_inf=V_inf,
                RPM=RPM,
                rho=rho,
                temperature=temperature
            )
        element.solve()
        forces[i, j, :] = element.forces()
        moments[i, j, :] = element.moments()

# Integrate the forces and moments over the blade span to obtain the thrust and torque
thrust = 0
torque = 0
for i in range(len(r)-1):
    dr = r[i+1]-r[i]
    for j in range(len(theta)-1):
        dtheta = theta[j+1]-theta[j]
        r_mid = r[i]+0.5*dr
        chord_mid = chord[i]+(chord[i+1]-chord[i])*(r_mid-r[i])/(r[i+1]-r[i])
        twist_mid = twist[i]+(twist[i+1]-twist[i])*(r_mid-r[i])/(r[i+1]-r[i])
        alpha_mid = alpha[i,j]+(alpha[i+1,j]-alpha[i,j])*(r_mid-r[i])/(r[i+1]-r[i])
        Re_mid = Re[i,j]+(Re[i+1,j]-Re[i,j])*(r_mid-r[i])/(r[i+1]-r[i])
        V_mid = np.sqrt(V_inf**2 + asb.tangential_induction_factor(0,RPM,rho,V_inf,diameter,r_mid,n_blades)**2)
        forces_mid,moments_mid = asb.solve_blade_element(
            r=r_mid,
            chord=chord_mid,
            twist=twist_mid,
            alpha=alpha_mid,
            Re=Re_mid,
            airfoil=airfoil,
            V=V_mid,
            rho=rho,
            n_blades=n_blades,
            rpm=RPM,
            method="iterative"
        )
        thrust += forces_mid[0]*dr*dtheta
        torque += moments_mid[2]*dr*dtheta

print(f"Thrust: {thrust:.2f} N")
print(f"Torque: {torque:.2f} N*m")