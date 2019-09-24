__author__ = "Pierre Cerantola"
__email__ = "cerantolap@eisti.eu"


## importing modules

import sys
from netCDF4 import Dataset
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import pyplot as plt


## defining global variables

parameters_number = 20
minimum_number_triplets_in_cell = 100
temperature_0_default_value = 0.001 # default electrons temperature
velocity_x1_default_value = 0.14 # default beam x velocity


## loading functions


# function for numeric input checking

def checkNumericEntry(input_text):
    if (input_text == ''):
        non_numeric = 1
    else:
        if (input_text == '.'):
            non_numeric = 1
        else:
            non_numeric = 0
            dot_counter = 0
            minus_counter = 0
            one_or_more_not_blank_detected = 0
            one_or_more_blank_detected = 0
            one_or_more_blank_after_not_blank_detected = 0
            one_or_more_not_blank_not_minus_not_dot_detected = 0
            i = 0
            while ((i < len(input_text)) & (non_numeric == 0)):
                if ((input_text[i] != '0') & (input_text[i] != '1') & (input_text[i] != '2') & (input_text[i] != '3') & (input_text[i] != '4') & (input_text[i] != '5') & (input_text[i] != '6') & (input_text[i] != '7') & (input_text[i] != '8') & (input_text[i] != '9') & (input_text[i] != '.') & (input_text[i] != ' ') & (input_text[i] != '-') & (input_text[i] != '\t')):
                    non_numeric = 1
                else:
                    if (input_text[i] == '.'):
                        dot_counter += 1
                        if ((dot_counter > 1) | (one_or_more_blank_after_not_blank_detected == 1)):
                            non_numeric = 1
                        else:
                            one_or_more_not_blank_detected = 1
                    elif ((input_text[i] == ' ') | (input_text[i] == '\t')):
                        if (one_or_more_not_blank_detected == 1):
                            one_or_more_blank_after_not_blank_detected = 1
                        else:
                            one_or_more_blank_detected = 1
                    elif (input_text[i] == '-'):
                        minus_counter += 1
                        if ((minus_counter > 1) | (one_or_more_not_blank_detected == 1)):
                            non_numeric = 1
                        else:
                            one_or_more_not_blank_detected = 1
                    else:
                        if (one_or_more_blank_after_not_blank_detected == 1):
                            non_numeric = 1
                        else:
                            one_or_more_not_blank_detected = 1
                            one_or_more_not_blank_not_minus_not_dot_detected = 1
                i += 1
            if (one_or_more_not_blank_not_minus_not_dot_detected == 0):
                non_numeric = 1
    return non_numeric


# function for console parameters checking

def checkConsoleParameters():
    if (len(sys.argv) == 2):
        if ((sys.argv[1] == "-h") | (sys.argv[1] == "--help")):
            print("How to use: \"python plasma_init_code.py input_config.txt output_plasma.nc [-d|--display]\"")
            return(1)
        else:
            print("Wrong input. Please type \"python plasma_init_code.py -h|--help\" to read how to use.")
            return(1)
    elif (len(sys.argv) == 4):
        if ((sys.argv[3] == "-d") | (sys.argv[3] == "--display")):
            return(0)
        else:
            print("Wrong input. Please type \"python plasma_init_code.py -h|--help\" to read how to use.")
            return(1)
    elif (len(sys.argv) == 3):
        return(0)
    else:
        print("Wrong input. Please type \"python plasma_init_code.py -h|--help\" to read how to use.")
        return(1)


# function for input configuration file structure checking

def checkConfigFileStructure(input_config, input_data):

    i = 0
    line_counter = 0
    non_blank_line_counter = 0
    input_file_error_counter = 0
    for line in input_config:
        if (i < parameters_number):
            fields = line.split("#")
            if (len(fields) == 2):
                check_numeric_entry = checkNumericEntry(fields[0])
                if (check_numeric_entry != 0):
                    input_file_error_counter += 1
                    non_blank_line_counter += 1
                    print("FATAL ERROR: parameter on line "+str(1+line_counter)+" of config file is a wrong input.")
                else:
                    input_data[i] = fields[0]
                    i += 1
                    non_blank_line_counter += 1
        line_counter += 1
    if (non_blank_line_counter < parameters_number):
        input_file_error_counter += 1
        print("FATAL ERROR: parameters_number lines of parameters expected in config file, but only "+str(non_blank_line_counter)+" detected.")

    input_config.close()

    if (input_file_error_counter == 0):
        return(0)
    else:
        return(1)


# function for input parameters coherence checking

def checkInputParametersCoherence(xout_len, yout_len, zout_len, nb_cells_xout, nb_cells_yout, nb_cells_zout, nb_cells_xin, nb_cells_yin, nb_cells_zin, nb_triplets_in_cell_average, sinusoidal_b_value, temperature_0, velocity_x1, charge_0_temp, charge_1_temp, charge_2_temp, mass_0_temp, mass_1_temp, mass_2_temp, distribution_type):

    # checking domain sizes values

    if (xout_len <= 0):
        print("FATAL ERROR: domain x length is lower or equal to 0.")
        return(1)
    if ((xout_len <= yout_len) | (yout_len <= 0)):
        if (xout_len <= yout_len):
            print("FATAL ERROR: domain y length is higher or equal to domain x length.")
            return(1)
        else:
            print("FATAL ERROR: domain y length is lower or equal to 0.")
            return(1)
    if ((xout_len <= zout_len) | (zout_len <= 0)):
        if (xout_len <= zout_len):
            print("FATAL ERROR: domain z length is higher or equal to domain x length.")
            return(1)
        else:
            print("FATAL ERROR: domain z length is lower or equal to 0.")
            return(1)


    # checking domain and subdomain cells numbers values

    if (nb_cells_xout <= 0):
        print("FATAL ERROR: domain x cells number is lower or equal to 0.")
        return(1)
    if (nb_cells_yout <= 0):
        print("FATAL ERROR: domain y cells number is lower or equal to 0.")
        return(1)
    if (nb_cells_xout <= nb_cells_yout):
        print("FATAL ERROR: domain y cells number is higher or equal to domain x cells number.")
        return(1)
    if (nb_cells_zout <= 0):
        print("FATAL ERROR: domain z cells number is lower or equal to 0.")
        return(1)
    if (nb_cells_xout <= nb_cells_zout):
        print("FATAL ERROR: domain z cells number is higher or equal to domain x cells number.")
        return(1)
    if (nb_cells_xin <= 0):
        print("FATAL ERROR: subdomain x cells number is lower or equal to 0.")
        return(1)
    if (nb_cells_xout <= nb_cells_xin):
        print("FATAL ERROR: subdomain x cells number is higher or equal to domain x cells number.")
        return(1)
    if (nb_cells_yout <= nb_cells_yin):
        print("FATAL ERROR: subdomain y cells number is higher or equal to domain y cells number.")
        return(1)
    if (nb_cells_yin >= nb_cells_xin):
        print("FATAL ERROR: subdomain y cells number is higher or equal to subdomain x cells number.")
        return(1)
    if (nb_cells_yin <= 0):
        print("FATAL ERROR: subdomain y cells number is lower or equal to 0.")
        return(1)
    if (nb_cells_zout <= nb_cells_zin):
        print("FATAL ERROR: subdomain z cells number is higher or equal to domain z cells number.")
        return(1)
    if (nb_cells_zin >= nb_cells_xin):
        print("FATAL ERROR: subdomain z cells number is higher or equal to subdomain x cells number.")
        return(1)
    if (nb_cells_zin <= 0):
        print("FATAL ERROR: subdomain z cells number is lower or equal to 0.")
        return(1)


    # checking average number of particles triplets in cells value

    if (nb_triplets_in_cell_average < minimum_number_triplets_in_cell):
        if (nb_triplets_in_cell_average > 0):
            print("FATAL ERROR: average number of particles triplets in cell is strictly lower than "+str(minimum_number_triplets_in_cell)+".")
            return(1)
        else:
            print("FATAL ERROR: average number of particles triplets in cell is lower or equal to 0.")
            return(1)


    # checking sinusoidal density function B value

    if (sinusoidal_b_value > 0.1):
        print("FATAL ERROR: sinusoidal density function B value is strictly higher than 0.1.")
        return(1)
    if (sinusoidal_b_value <= 0):
        print("FATAL ERROR: sinusoidal density function B value is lower or equal to 0.")
        return(1)


    # checking particles charges values

    if ((2*charge_0_temp + charge_1_temp + charge_2_temp) != 0):
        print("FATAL ERROR: 2*electron_charge + beam_charge + ion_charge is not equal to 0.")
        return(1)


    # checking electrons distribution type

    if ((distribution_type != 1) & (distribution_type != 2)):
        print("FATAL ERROR: bad electrons distribution type input.")
        return(1)

    return(0)


# function for particles coordinates computing

def computeParticlesCoordinates(distribution_type, nb_triplets_in_cell_average, sinusoidal_b_value, particles_0_counter, particles_1_counter, particles_2_counter, particles_counters, nb_cells_xin, nb_cells_yin, nb_cells_zin, cell_size_x, cell_size_y, cell_size_z, subdomain_start_x, subdomain_start_y, subdomain_start_z, coordinates_x0_excessive, coordinates_y0_excessive, coordinates_z0_excessive, coordinates_x1_excessive, coordinates_y1_excessive, coordinates_z1_excessive, coordinates_x2_excessive, coordinates_y2_excessive, coordinates_z2_excessive):

    for i in range(nb_cells_xin):
        bound_low_x = i*cell_size_x+subdomain_start_x
        bound_high_x = (i+1)*cell_size_x+subdomain_start_x

        if (distribution_type == 1):
            nb_triplets_in_current_cell = nb_triplets_in_cell_average
        else:
            nb_triplets_in_current_cell = int((1+sinusoidal_b_value*np.cos(2*np.pi*i/nb_cells_xin))*nb_triplets_in_cell_average)

        for j in range(nb_cells_yin):
            bound_low_y = j*cell_size_y+subdomain_start_y
            bound_high_y = (j+1)*cell_size_y+subdomain_start_y

            for k in range(nb_cells_zin):
                bound_low_z = k*cell_size_z+subdomain_start_z
                bound_high_z = (k+1)*cell_size_z+subdomain_start_z

                random_sample_uniform_x = np.random.uniform(low=bound_low_x, high=bound_high_x, size=(nb_triplets_in_current_cell,))
                random_sample_uniform_y = np.random.uniform(low=bound_low_y, high=bound_high_y, size=(nb_triplets_in_current_cell,))
                random_sample_uniform_z = np.random.uniform(low=bound_low_z, high=bound_high_z, size=(nb_triplets_in_current_cell,))

                if (distribution_type == 2):
                    random_sample_sinusoidal_x = np.random.uniform(low=bound_low_x, high=bound_high_x, size=(nb_triplets_in_current_cell,))
                    random_sample_sinusoidal_y = np.random.uniform(low=bound_low_y, high=bound_high_y, size=(nb_triplets_in_current_cell,))
                    random_sample_sinusoidal_z = np.random.uniform(low=bound_low_z, high=bound_high_z, size=(nb_triplets_in_current_cell,))

                for p in range(2*nb_triplets_in_current_cell):
                    if (distribution_type == 1):
                        coordinates_x0_excessive[particles_0_counter+p] = random_sample_uniform_x[int(p/2)]
                        coordinates_y0_excessive[particles_0_counter+p] = random_sample_uniform_y[int(p/2)]
                        coordinates_z0_excessive[particles_0_counter+p] = random_sample_uniform_z[int(p/2)]
                    else:
                        coordinates_x0_excessive[particles_0_counter+p] = random_sample_sinusoidal_x[int(p/2)]
                        coordinates_y0_excessive[particles_0_counter+p] = random_sample_sinusoidal_y[int(p/2)]
                        coordinates_z0_excessive[particles_0_counter+p] = random_sample_sinusoidal_z[int(p/2)]
                particles_0_counter += 2*nb_triplets_in_current_cell

                if (distribution_type == 1):
                    for p in range(nb_triplets_in_current_cell):
                        coordinates_x1_excessive[particles_1_counter+p] = random_sample_uniform_x[p]
                        coordinates_y1_excessive[particles_1_counter+p] = random_sample_uniform_y[p]
                        coordinates_z1_excessive[particles_1_counter+p] = random_sample_uniform_z[p]
                    particles_1_counter += nb_triplets_in_current_cell

                for p in range(nb_triplets_in_current_cell):
                    coordinates_x2_excessive[particles_2_counter+p] = random_sample_uniform_x[p]
                    coordinates_y2_excessive[particles_2_counter+p] = random_sample_uniform_y[p]
                    coordinates_z2_excessive[particles_2_counter+p] = random_sample_uniform_z[p]
                particles_2_counter += nb_triplets_in_current_cell
    if (distribution_type == 2):
        coordinates_x1_excessive[0] = coordinates_x0_excessive[0]
        coordinates_y1_excessive[0] = coordinates_y0_excessive[0]
        coordinates_z1_excessive[0] = coordinates_z0_excessive[0]
        particles_1_counter = 1

    particles_counters[0] = particles_0_counter
    particles_counters[1] = particles_1_counter
    particles_counters[2] = particles_2_counter


# function for particles impulses computing

def computeParticlesImpulses(dim_0_len, distribution_type, mass_1_temp, mass_0_temp, velocity_x1, temperature_0, impulses_x0_temp, impulses_y0_temp, impulses_z0_temp, impulses_x1_temp):

    gauss_stand_dev_0 = temperature_0/2.355 # 2.355 is the FWHM factor
    i = 0

    while (i < dim_0_len):

        thermal_velocity_0 = np.random.normal(loc = 0.0, scale = gauss_stand_dev_0, size = None)
        velocity_y0 = np.random.normal(loc = 0.0, scale = gauss_stand_dev_0, size = None)
        velocity_z0 = np.random.normal(loc = 0.0, scale = gauss_stand_dev_0, size = None)

        if (distribution_type == 1):
            if (i%2 == 0):
                velocity_x0 = -(mass_1_temp/mass_0_temp)*velocity_x1/2+thermal_velocity_0
            else:
                velocity_x0 = -(mass_1_temp/mass_0_temp)*velocity_x1/2-thermal_velocity_0

        else:
            if (i%2 == 0):
                velocity_x0 = thermal_velocity_0
            else:
                velocity_x0 = -thermal_velocity_0

        if ((velocity_x0**2+velocity_y0**2+velocity_z0**2) >= 1):
            if (distribution_type == 1):
                print("\nWARNING: due to input Te and Vbx, at least one of Vex magnitude is higher than 1.\nAs a consequence, Te and Vbx have been replaced by default values: Te = "+str(temperature_0_default_value)+" and Vbx = "+str(velocity_x1_default_value)+".")

                temperature_0 = temperature_0_default_value
                velocity_x1 = velocity_x1_default_value

                print("\nINFO: computing data, please wait...")

                for j in range(dim_1_len):
                    impulses_x1_temp[j] = velocity_x1/np.sqrt(1-velocity_x1**2)

            else:
                print("\nWARNING: due to input Te, at least one of Vex magnitude is higher than 1.\nAs a consequence, Te have been replaced by default value: Te = "+str(temperature_0_default_value)+".")

                temperature_0 = temperature_0_default_value

                print("\nINFO: computing data, please wait...")

            gauss_stand_dev_0 = temperature_0/2.355 # 2.355 is the FWHM factor
            i = 0

        else:

            gamma_0 = 1/np.sqrt(1-velocity_x0**2-velocity_y0**2-velocity_z0**2)

            impulses_x0_temp[i] = velocity_x0*gamma_0
            impulses_y0_temp[i] = velocity_y0*gamma_0
            impulses_z0_temp[i] = velocity_z0*gamma_0

            i += 1


# function for NetCDF dimensions adding

def addDimensionsNetCDF(nb_cells_xout, nb_cells_yout, nb_cells_zout, dim_0_len, dim_1_len, dim_2_len):
    plasma_write.createDimension('x', nb_cells_xout)
    plasma_write.createDimension('y', nb_cells_yout)
    plasma_write.createDimension('z', nb_cells_zout)
    plasma_write.createDimension('0_DIM', dim_0_len)
    plasma_write.createDimension('1_DIM', dim_1_len)
    plasma_write.createDimension('2_DIM', dim_2_len)


# function for NetCDF variables attributes adding

def addAttributesNetCDFVariables(ex, ey, ez, mx, my, mz, jx, jy, jz, qx, qy, qz, extra_number_0, nb_particles_0, charge_0, mass_0, coordinates_x0, coordinates_y0, coordinates_z0, impulses_x0, impulses_y0, impulses_z0, extra_number_1, nb_particles_1, charge_1, mass_1, coordinates_x1, coordinates_y1, coordinates_z1, impulses_x1, impulses_y1, impulses_z1, extra_number_2, nb_particles_2, charge_2, mass_2, coordinates_x2, coordinates_y2, coordinates_z2, impulses_x2, impulses_y2, impulses_z2):

    ex.units = 'N.C^-1'
    ex.description = 'electric field, Ex'
    ey.units = 'N.C^-1'
    ey.description = 'electric field, Ey'
    ez.units = 'N.C^-1'
    ez.description = 'electric field, Ez'

    mx.units = 'T'
    mx.description = 'magnetic field, Mx'
    my.units = 'T'
    my.description = 'magnetic field, My'
    mz.units = 'T'
    mz.description = 'magnetic field, Mz'

    jx.units = 'no units'
    jx.description = 'current, Jx'
    jy.units = 'no units'
    jy.description = 'current, Jy'
    jz.units = 'no units'
    jz.description = 'current, Jz'

    qx.units = 'no units'
    qx.description = 'magnetic field at halfstep, Qx'
    qy.units = 'no units'
    qy.description = 'magnetic field at halfstep, Qy'
    qz.units = 'no units'
    qz.description = 'magnetic field at halfstep, Qz'

    extra_number_0.units = 'no units'
    extra_number_0.description = 'extra number placed by Fortran'
    nb_particles_0.units = 'N^-1'
    nb_particles_0.description = 'number of particles of sort 0'
    charge_0.units = 'C'
    charge_0.description = 'charge for sort 0'
    mass_0.units = ''
    mass_0.description = 'mass for sort 0'
    coordinates_x0.units = 'no units'
    coordinates_x0.description = 'x coordinates for particles of sort 0'
    coordinates_y0.units = 'no units'
    coordinates_y0.description = 'y coordinates for particles of sort 0'
    coordinates_z0.units = 'no units'
    coordinates_z0.description = 'z coordinates for particles of sort 0'
    impulses_x0.units = 'N.s'
    impulses_x0.description = 'x impulses for particles of sort 0'
    impulses_y0.units = 'N.s'
    impulses_y0.description = 'y impulses for particles of sort 0'
    impulses_z0.units = 'N.s'
    impulses_z0.description = 'z impulses for particles of sort 0'

    extra_number_1.units = 'no units'
    extra_number_1.description = 'extra number placed by Fortran'
    nb_particles_1.units = 'N^-1'
    nb_particles_1.description = 'number of particles of sort 1'
    charge_1.units = 'C'
    charge_1.description = 'charge for sort 1'
    mass_1.units = ''
    mass_1.description = 'mass for sort 1'
    coordinates_x1.units = 'no units'
    coordinates_x1.description = 'x coordinates for particles of sort 1'
    coordinates_y1.units = 'no units'
    coordinates_y1.description = 'y coordinates for particles of sort 1'
    coordinates_z1.units = 'no units'
    coordinates_z1.description = 'z coordinates for particles of sort 1'
    impulses_x1.units = 'N.s'
    impulses_x1.description = 'x impulses for particles of sort 1'
    impulses_y1.units = 'N.s'
    impulses_y1.description = 'y impulses for particles of sort 1'
    impulses_z1.units = 'N.s'
    impulses_z1.description = 'z impulses for particles of sort 1'

    extra_number_2.units = 'no units'
    extra_number_2.description = 'extra number placed by Fortran'
    nb_particles_2.units = 'N^-1'
    nb_particles_2.description = 'number of particles of sort 2'
    charge_2.units = 'C'
    charge_2.description = 'charge for sort 2'
    mass_2.units = ''
    mass_2.description = 'mass for sort 2'
    coordinates_x2.units = 'no units'
    coordinates_x2.description = 'x coordinates for particles of sort 2'
    coordinates_y2.units = 'no units'
    coordinates_y2.description = 'y coordinates for particles of sort 2'
    coordinates_z2.units = 'no units'
    coordinates_z2.description = 'z coordinates for particles of sort 2'
    impulses_x2.units = 'N.s'
    impulses_x2.description = 'x impulses for particles of sort 2'
    impulses_y2.units = 'N.s'
    impulses_y2.description = 'y impulses for particles of sort 2'
    impulses_z2.units = 'N.s'
    impulses_z2.description = 'z impulses for particles of sort 2'


# function for NetCDF data saving

def saveNetCDFFile(ex, ey, ez, mx, my, mz, jx, jy, jz, qx, qy, qz, ex_temp, ey_temp, ez_temp, mx_temp, my_temp, mz_temp, jx_temp, jy_temp, jz_temp, qx_temp, qy_temp, qz_temp, extra_number_0, extra_number_1, extra_number_2, extra_number_0_temp, extra_number_1_temp, extra_number_2_temp, nb_particles_0, nb_particles_1, nb_particles_2, dim_0_len, dim_1_len, dim_2_len, charge_0, charge_1, charge_2, charge_0_temp, charge_1_temp, charge_2_temp, mass_0, mass_1, mass_2, mass_0_temp, mass_1_temp, mass_2_temp, coordinates_x0, coordinates_y0, coordinates_z0, coordinates_x1, coordinates_y1, coordinates_z1, coordinates_x2, coordinates_y2, coordinates_z2, coordinates_x0_temp, coordinates_y0_temp, coordinates_z0_temp, coordinates_x1_temp, coordinates_y1_temp, coordinates_z1_temp, coordinates_x2_temp, coordinates_y2_temp, coordinates_z2_temp, impulses_x0, impulses_y0, impulses_z0, impulses_x1, impulses_y1, impulses_z1, impulses_x2, impulses_y2, impulses_z2, impulses_x0_temp, impulses_y0_temp, impulses_z0_temp, impulses_x1_temp, impulses_y1_temp, impulses_z1_temp, impulses_x2_temp, impulses_y2_temp, impulses_z2_temp):

    ex[:] = ex_temp
    ey[:] = ey_temp
    ez[:] = ez_temp

    mx[:] = mx_temp
    my[:] = my_temp
    mz[:] = mz_temp

    jx[:] = jx_temp
    jy[:] = jy_temp
    jz[:] = jz_temp

    qx[:] = qx_temp
    qy[:] = qy_temp
    qz[:] = qz_temp

    extra_number_0[:] = extra_number_0_temp
    nb_particles_0[:] = dim_0_len
    charge_0[:] = charge_0_temp
    mass_0[:] = mass_0_temp
    coordinates_x0[:] = coordinates_x0_temp
    coordinates_y0[:] = coordinates_y0_temp
    coordinates_z0[:] = coordinates_z0_temp
    impulses_x0[:] = impulses_x0_temp
    impulses_y0[:] = impulses_y0_temp
    impulses_z0[:] = impulses_z0_temp

    extra_number_1[:] = extra_number_1_temp
    nb_particles_1[:] = dim_1_len
    charge_1[:] = charge_1_temp
    mass_1[:] = mass_1_temp
    coordinates_x1[:] = coordinates_x1_temp
    coordinates_y1[:] = coordinates_y1_temp
    coordinates_z1[:] = coordinates_z1_temp
    impulses_x1[:] = impulses_x1_temp
    impulses_y1[:] = impulses_y1_temp
    impulses_z1[:] = impulses_z1_temp

    extra_number_2[:] = extra_number_2_temp
    nb_particles_2[:] = dim_2_len
    charge_2[:] = charge_2_temp
    mass_2[:] = mass_2_temp
    coordinates_x2[:] = coordinates_x2_temp
    coordinates_y2[:] = coordinates_y2_temp
    coordinates_z2[:] = coordinates_z2_temp
    impulses_x2[:] = impulses_x2_temp
    impulses_y2[:] = impulses_y2_temp
    impulses_z2[:] = impulses_z2_temp


# function for generated plasma plotting or not

def plotOrNotGeneratedPlasma(sys_argv, coordinates_x0_temp, coordinates_y0_temp, coordinates_z0_temp, coordinates_x1_temp, coordinates_y1_temp, coordinates_z1_temp, coordinates_x2_temp, coordinates_y2_temp, coordinates_z2_temp):

    if (len(sys_argv) == 4):

        if ((sys_argv[3] == "-d") | (sys_argv[3] == "--display")):

            print("\nINFO: generating data plot, please wait...\n")


            # setting axes and plot attributes

            fig = plt.figure()
            ax = fig.add_subplot(111, projection = '3d')

            ax.set_title('Initial plasma particles triplets configuration')
            ax.set_xlabel('domain x axis')
            ax.set_ylabel('domain y axis')
            ax.set_zlabel('domain z axis')

            ax.axes.set_xlim3d(0, xout_len)
            ax.axes.set_ylim3d(0, yout_len)
            ax.axes.set_zlim3d(0, zout_len)


            # adding particles triplets to the 3D plot

            if (distribution_type == 1):
                ax.scatter3D(coordinates_x1_temp, coordinates_y1_temp, coordinates_z1_temp, s = 5, c = "navy")
            else:
                coordinates_x0_temp_reshaped = coordinates_x0_temp[::2]
                coordinates_y0_temp_reshaped = coordinates_y0_temp[::2]
                coordinates_z0_temp_reshaped = coordinates_z0_temp[::2]
                ax.scatter3D(coordinates_x2_temp, coordinates_y2_temp, coordinates_z2_temp, s = 5, c = "navy")
                ax.scatter3D(coordinates_x0_temp_reshaped, coordinates_y0_temp_reshaped, coordinates_z0_temp_reshaped, s = 5, c = "navy")

            plt.show()

            print("INFO: program ended correctly.")

        else:
            print("\nINFO: program ended correctly.")
    else:
        print("\nINFO: program ended correctly.")


## MAIN


print("")


# checking console parameters

check_console_parameters = checkConsoleParameters()

if (check_console_parameters == 0):

    # reading input config and creating ouput NetCDF plasma file

    input_config = open(sys.argv[1])
    plasma_write = Dataset(sys.argv[2], "w", format = "NETCDF4")


    # checking config file structure

    input_data = np.zeros(parameters_number)
    check_config_file_structure = checkConfigFileStructure(input_config, input_data)

    if (check_config_file_structure == 0):

        # extracting input data from config file

        xout_len = float(input_data[0])
        yout_len = float(input_data[1])
        zout_len = float(input_data[2])
        nb_cells_xout = int(input_data[3])
        nb_cells_yout = int(input_data[4])
        nb_cells_zout = int(input_data[5])
        nb_cells_xin = int(input_data[6])
        nb_cells_yin = int(input_data[7])
        nb_cells_zin = int(input_data[8])
        nb_triplets_in_cell_average = int(input_data[9])
        sinusoidal_b_value = float(input_data[10])
        temperature_0 = float(input_data[11])
        velocity_x1 = float(input_data[12])
        charge_0_temp = float(input_data[13])
        charge_1_temp = float(input_data[14])
        charge_2_temp = float(input_data[15])
        mass_0_temp = float(input_data[16])
        mass_1_temp = float(input_data[17])
        mass_2_temp = float(input_data[18])
        distribution_type = int(input_data[19])


        # checking config parameters coherence

        check_input_parameters_coherence = checkInputParametersCoherence(xout_len, yout_len, zout_len, nb_cells_xout, nb_cells_yout, nb_cells_zout, nb_cells_xin, nb_cells_yin, nb_cells_zin, nb_triplets_in_cell_average, sinusoidal_b_value, temperature_0, velocity_x1, charge_0_temp, charge_1_temp, charge_2_temp, mass_0_temp, mass_1_temp, mass_2_temp, distribution_type)

        if (check_input_parameters_coherence == 0):

            print("INFO: computing data, please wait...")


            # computing total number of subdomain cells

            nb_cells_subdomain = nb_cells_xin*nb_cells_yin*nb_cells_zin


            # computing excessive 0_DIM, 1_DIM and 2_DIM

            dim_2_excessive_len = nb_triplets_in_cell_average*nb_cells_subdomain
            if (distribution_type == 1):
                dim_1_excessive_len = dim_2_excessive_len
            else:
                dim_1_excessive_len = 1
            dim_0_excessive_len = 2*dim_2_excessive_len


            # computing cell size for each axis

            cell_size_x = xout_len/nb_cells_xout
            cell_size_y = yout_len/nb_cells_yout
            cell_size_z = zout_len/nb_cells_zout


            # computing subdomain start coordinates for each axis

            subdomain_start_x = ((nb_cells_xout-nb_cells_xin)/2)*cell_size_x
            subdomain_start_y = ((nb_cells_yout-nb_cells_yin)/2)*cell_size_y
            subdomain_start_z = ((nb_cells_zout-nb_cells_zin)/2)*cell_size_z


            # computing extra numbers

            extra_number_0_temp = 24
            extra_number_1_temp = 24
            extra_number_2_temp = 24


            # computing electric arrays

            ex_temp = np.zeros((nb_cells_xout, nb_cells_yout, nb_cells_zout))
            ey_temp = np.zeros((nb_cells_xout, nb_cells_yout, nb_cells_zout))
            ez_temp = np.zeros((nb_cells_xout, nb_cells_yout, nb_cells_zout))


            # computing magnetic arrays

            mx_temp = np.zeros((nb_cells_xout, nb_cells_yout, nb_cells_zout))
            my_temp = np.zeros((nb_cells_xout, nb_cells_yout, nb_cells_zout))
            mz_temp = np.zeros((nb_cells_xout, nb_cells_yout, nb_cells_zout))


            # computing current arrays

            jx_temp = np.zeros((nb_cells_xout, nb_cells_yout, nb_cells_zout))
            jy_temp = np.zeros((nb_cells_xout, nb_cells_yout, nb_cells_zout))
            jz_temp = np.zeros((nb_cells_xout, nb_cells_yout, nb_cells_zout))


            # computing magnetic field at halfstep arrays

            qx_temp = np.zeros((nb_cells_xout, nb_cells_yout, nb_cells_zout))
            qy_temp = np.zeros((nb_cells_xout, nb_cells_yout, nb_cells_zout))
            qz_temp = np.zeros((nb_cells_xout, nb_cells_yout, nb_cells_zout))


            # computing excessive coordinates arrays

            coordinates_x0_excessive = np.zeros(dim_0_excessive_len)
            coordinates_y0_excessive = np.zeros(dim_0_excessive_len)
            coordinates_z0_excessive = np.zeros(dim_0_excessive_len)

            coordinates_x1_excessive = np.zeros(dim_1_excessive_len)
            coordinates_y1_excessive = np.zeros(dim_1_excessive_len)
            coordinates_z1_excessive = np.zeros(dim_1_excessive_len)

            coordinates_x2_excessive = np.zeros(dim_2_excessive_len)
            coordinates_y2_excessive = np.zeros(dim_2_excessive_len)
            coordinates_z2_excessive = np.zeros(dim_2_excessive_len)

            particles_0_counter = 0
            particles_1_counter = 0
            particles_2_counter = 0

            particles_counters = np.zeros(3)

            computeParticlesCoordinates(distribution_type, nb_triplets_in_cell_average, sinusoidal_b_value, particles_0_counter, particles_1_counter, particles_2_counter, particles_counters, nb_cells_xin, nb_cells_yin, nb_cells_zin, cell_size_x, cell_size_y, cell_size_z, subdomain_start_x, subdomain_start_y, subdomain_start_z, coordinates_x0_excessive, coordinates_y0_excessive, coordinates_z0_excessive, coordinates_x1_excessive, coordinates_y1_excessive, coordinates_z1_excessive, coordinates_x2_excessive, coordinates_y2_excessive, coordinates_z2_excessive)


            # computing real 0_DIM, 1_DIM and 2_DIM

            dim_0_len = int(particles_counters[0])
            dim_1_len = int(particles_counters[1])
            dim_2_len = int(particles_counters[2])


            # computing real coordinates arrays

            coordinates_x0_temp = coordinates_x0_excessive[:dim_0_len]
            coordinates_y0_temp = coordinates_y0_excessive[:dim_0_len]
            coordinates_z0_temp = coordinates_z0_excessive[:dim_0_len]

            coordinates_x1_temp = coordinates_x1_excessive[:dim_1_len]
            coordinates_y1_temp = coordinates_y1_excessive[:dim_1_len]
            coordinates_z1_temp = coordinates_z1_excessive[:dim_1_len]

            coordinates_x2_temp = coordinates_x2_excessive[:dim_2_len]
            coordinates_y2_temp = coordinates_y2_excessive[:dim_2_len]
            coordinates_z2_temp = coordinates_z2_excessive[:dim_2_len]


            # computing velocities and then impulses arrays

            impulses_x0_temp = np.zeros(dim_0_len)
            impulses_y0_temp = np.zeros(dim_0_len)
            impulses_z0_temp = np.zeros(dim_0_len)

            if (distribution_type == 1):
                impulses_x1_temp = np.full(dim_1_len, velocity_x1/np.sqrt(1-velocity_x1**2))
            else:
                impulses_x1_temp = np.zeros(dim_1_len)
            impulses_y1_temp = np.zeros(dim_1_len)
            impulses_z1_temp = np.zeros(dim_1_len)

            impulses_x2_temp = np.zeros(dim_2_len)
            impulses_y2_temp = np.zeros(dim_2_len)
            impulses_z2_temp = np.zeros(dim_2_len)

            computeParticlesImpulses(dim_0_len, distribution_type, mass_1_temp, mass_0_temp, velocity_x1, temperature_0, impulses_x0_temp, impulses_y0_temp, impulses_z0_temp, impulses_x1_temp)


            # adding dimensions to the NetCDF plasma file

            addDimensionsNetCDF(nb_cells_xout, nb_cells_yout, nb_cells_zout, dim_0_len, dim_1_len, dim_2_len)


            # adding variables to the NetCDF plasma file

            ex = plasma_write.createVariable('Ex', 'f8', ('x', 'y', 'z'))
            ey = plasma_write.createVariable('Ey', 'f8', ('x', 'y', 'z'))
            ez = plasma_write.createVariable('Ez', 'f8', ('x', 'y', 'z'))

            mx = plasma_write.createVariable('Mx', 'f8', ('x', 'y', 'z'))
            my = plasma_write.createVariable('My', 'f8', ('x', 'y', 'z'))
            mz = plasma_write.createVariable('Mz', 'f8', ('x', 'y', 'z'))

            jx = plasma_write.createVariable('Jx', 'f8', ('x', 'y', 'z'))
            jy = plasma_write.createVariable('Jy', 'f8', ('x', 'y', 'z'))
            jz = plasma_write.createVariable('Jz', 'f8', ('x', 'y', 'z'))

            qx = plasma_write.createVariable('Qx', 'f8', ('x', 'y', 'z'))
            qy = plasma_write.createVariable('Qy', 'f8', ('x', 'y', 'z'))
            qz = plasma_write.createVariable('Qz', 'f8', ('x', 'y', 'z'))

            extra_number_0 = plasma_write.createVariable('Extra_number_0', 'i')
            nb_particles_0 = plasma_write.createVariable('Nb_particles_0', 'i')
            charge_0 = plasma_write.createVariable('Charge_0', 'f8')
            mass_0 = plasma_write.createVariable('Mass_0', 'f8')
            coordinates_x0 = plasma_write.createVariable('Coordinates_x0', 'f8', ('0_DIM'))
            coordinates_y0 = plasma_write.createVariable('Coordinates_y0', 'f8', ('0_DIM'))
            coordinates_z0 = plasma_write.createVariable('Coordinates_z0', 'f8', ('0_DIM'))
            impulses_x0 = plasma_write.createVariable('Impulses_x0', 'f8', ('0_DIM'))
            impulses_y0 = plasma_write.createVariable('Impulses_y0', 'f8', ('0_DIM'))
            impulses_z0 = plasma_write.createVariable('Impulses_z0', 'f8', ('0_DIM'))

            extra_number_1 = plasma_write.createVariable('Extra_number_1', 'i')
            nb_particles_1 = plasma_write.createVariable('Nb_particles_1', 'i')
            charge_1 = plasma_write.createVariable('Charge_1', 'f8')
            mass_1 = plasma_write.createVariable('Mass_1', 'f8')
            coordinates_x1 = plasma_write.createVariable('Coordinates_x1', 'f8', ('1_DIM'))
            coordinates_y1 = plasma_write.createVariable('Coordinates_y1', 'f8', ('1_DIM'))
            coordinates_z1 = plasma_write.createVariable('Coordinates_z1', 'f8', ('1_DIM'))
            impulses_x1 = plasma_write.createVariable('Impulses_x1', 'f8', ('1_DIM'))
            impulses_y1 = plasma_write.createVariable('Impulses_y1', 'f8', ('1_DIM'))
            impulses_z1 = plasma_write.createVariable('Impulses_z1', 'f8', ('1_DIM'))

            extra_number_2 = plasma_write.createVariable('Extra_number_2', 'i')
            nb_particles_2 = plasma_write.createVariable('Nb_particles_2', 'i')
            charge_2 = plasma_write.createVariable('Charge_2', 'f8')
            mass_2 = plasma_write.createVariable('Mass_2', 'f8')
            coordinates_x2 = plasma_write.createVariable('Coordinates_x2', 'f8', ('2_DIM'))
            coordinates_y2 = plasma_write.createVariable('Coordinates_y2', 'f8', ('2_DIM'))
            coordinates_z2 = plasma_write.createVariable('Coordinates_z2', 'f8', ('2_DIM'))
            impulses_x2 = plasma_write.createVariable('Impulses_x2', 'f8', ('2_DIM'))
            impulses_y2 = plasma_write.createVariable('Impulses_y2', 'f8', ('2_DIM'))
            impulses_z2 = plasma_write.createVariable('Impulses_z2', 'f8', ('2_DIM'))


            # adding attributes to the variables

            addAttributesNetCDFVariables(ex, ey, ez, mx, my, mz, jx, jy, jz, qx, qy, qz, extra_number_0, nb_particles_0, charge_0, mass_0, coordinates_x0, coordinates_y0, coordinates_z0, impulses_x0, impulses_y0, impulses_z0, extra_number_1, nb_particles_1, charge_1, mass_1, coordinates_x1, coordinates_y1, coordinates_z1, impulses_x1, impulses_y1, impulses_z1, extra_number_2, nb_particles_2, charge_2, mass_2, coordinates_x2, coordinates_y2, coordinates_z2, impulses_x2, impulses_y2, impulses_z2)


            # writing variables in the NetCDF plasma file

            saveNetCDFFile(ex, ey, ez, mx, my, mz, jx, jy, jz, qx, qy, qz, ex_temp, ey_temp, ez_temp, mx_temp, my_temp, mz_temp, jx_temp, jy_temp, jz_temp, qx_temp, qy_temp, qz_temp, extra_number_0, extra_number_1, extra_number_2, extra_number_0_temp, extra_number_1_temp, extra_number_2_temp, nb_particles_0, nb_particles_1, nb_particles_2, dim_0_len, dim_1_len, dim_2_len, charge_0, charge_1, charge_2, charge_0_temp, charge_1_temp, charge_2_temp, mass_0, mass_1, mass_2, mass_0_temp, mass_1_temp, mass_2_temp, coordinates_x0, coordinates_y0, coordinates_z0, coordinates_x1, coordinates_y1, coordinates_z1, coordinates_x2, coordinates_y2, coordinates_z2, coordinates_x0_temp, coordinates_y0_temp, coordinates_z0_temp, coordinates_x1_temp, coordinates_y1_temp, coordinates_z1_temp, coordinates_x2_temp, coordinates_y2_temp, coordinates_z2_temp, impulses_x0, impulses_y0, impulses_z0, impulses_x1, impulses_y1, impulses_z1, impulses_x2, impulses_y2, impulses_z2, impulses_x0_temp, impulses_y0_temp, impulses_z0_temp, impulses_x1_temp, impulses_y1_temp, impulses_z1_temp, impulses_x2_temp, impulses_y2_temp, impulses_z2_temp)


            # closing the NetCDF plasma file

            plasma_write.close()


            # plot or not generated plasma

            plotOrNotGeneratedPlasma(sys.argv, coordinates_x0_temp, coordinates_y0_temp, coordinates_z0_temp, coordinates_x1_temp, coordinates_y1_temp, coordinates_z1_temp, coordinates_x2_temp, coordinates_y2_temp, coordinates_z2_temp)