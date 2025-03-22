from Data import matakuliah, prodi, dosen, ruang, waktu, kelas,keilmuan
from Struktur import Matakuliah, Prodi, Dosen, Ruang, Waktu, Kelas
import random
import os
import pandas as pd

matakuliah_list = [
    Matakuliah(
        i.split(sep="\t")[1],
        i.split(sep="\t")[2],
        i.split(sep="\t")[3],
        i.split(sep="\t")[4],
        i.split(sep="\t")[5].split(sep=";"),
        i.split(sep="\t")[6],
        i.split(sep="\t")[7],
    ) for i in matakuliah.split(sep="\n")
]

prodi_list = [
    Prodi(
        i.split(sep="\t")[1],
        i.split(sep="\t")[2],
        i.split(sep="\t")[3],
    ) for i in prodi.split(sep="\n")
]

dosen_list = [
    Dosen(
        i.split(sep="\t")[0],
        ["Sistem Informasi"]+random.sample(keilmuan, 5),
        i.split(sep="\t")[2],
        i.split(sep="\t")[3],
        i.split(sep="\t")[4],
    ) for i in dosen.split(sep="\n")
]

ruang_list = [
    Ruang(
        i.split(sep="\t")[1],
        i.split(sep="\t")[2],
        i.split(sep="\t")[3],
        i.split(sep="\t")[4],
    ) for i in ruang.split(sep="\n")
]

waktu_list = [
    Waktu(
        i.split(sep="\t")[0],
        i.split(sep="\t")[1],
    ) for i in waktu.split(sep="\n")
]

waktu_list = [
    Waktu(
        i.split(sep="\t")[0],
        i.split(sep="\t")[1],
    ) for i in waktu.split(sep="\n")
]

kelas_list = [
    Kelas(
        i.split(sep="\t")[0],
        i.split(sep="\t")[1],
    ) for i in kelas.split(sep="\n")
]

def seeds():
    mk = random.choice(matakuliah_list)

    adj = [i for i in dosen_list if i.prodi == mk.prodi]

    choice_of_lecturer = [
        lec.lower() for lec in dosen_list
        if any(keilmuan.lower() in mk.keilmuan for keilmuan in lec.keilmuan)
    ]
    if (len(choice_of_lecturer) == 0):
        choice_of_lecturer = [
        lec.lower() for lec in dosen_list
        if any(keilmuan.lower() in mk.keilmuan for keilmuan in lec.keilmuan)
    ]
    for_addition = 3 - len(choice_of_lecturer)
    filtered_dosen = [i for i in dosen_list if i not in choice_of_lecturer]
    addition= []
    if len(filtered_dosen) > 0:
        addition = random.sample(filtered_dosen, for_addition)

    lec = choice_of_lecturer+addition
    room = [i for i in ruang_list if mk.model.lower() == i.model.lower()]
    if (len(room) > 0):
        room = random.sample(room,1)
    time = random.choice(waktu_list)

    kelompok = [i for i in kelas_list if i.semester == mk.semester]
    # kel = []
    # if len(kelompok) > 0:
    kel  = random.sample([i.kelas for i in kelompok], 1)
    result = [mk, lec,room,kel[0],time.hari, time.menit]
    return result

def show(item):
    return (
        item[0].nama,
        item[0].sks,
        item[0].semester,
        item[0].model,
        [i.nama for i in item[1]],
        item[2][0].kode,
        item[3],
        item[4],
        convert_minutes_to_time(item[5])
        )

def check_fitness(indv):
    fitnesses = []

    for individu in indv:
        cmk = set()  # Conflicting courses
        cr = set()   # Conflicting rooms
        cd = set()   # Conflicting lecturers
        ck = set()   # Conflicting class groups

        scanned_dosen = set()  # Track already scanned lecturers

        for kromosom1 in individu:
            course = kromosom1[0]
            lecturers = kromosom1[1]
            room = kromosom1[2][0] if kromosom1[2] else None
            class_group = kromosom1[3]
            day = kromosom1[4]
            start_time = kromosom1[5]
            end_time = start_time + 50 * int(course.sks)

            # Track lecturer conflicts for this kromosom
            lecturer_conflicts = {lec: 0 for lec in lecturers}

            for kromosom2 in individu:
                if kromosom1 == kromosom2:
                    continue

                course2 = kromosom2[0]
                lecturers2 = kromosom2[1]
                room2 = kromosom2[2][0] if kromosom2[2] else None
                class_group2 = kromosom2[3]
                day2 = kromosom2[4]
                start_time2 = kromosom2[5]
                end_time2 = start_time2 + 50 * int(course2.sks)

                # Check course conflicts (same code, same study group)
                if course.kode == course2.kode and class_group == class_group2:
                    cmk.add(course.kode)

                # Overlapping schedule for the same course
                if (course.kode == course2.kode and day == day2 and
                        start_time2 < end_time and start_time2 >= start_time):
                    cmk.add(course.kode)

                # Class group conflicts
                if (class_group == class_group2 and day == day2 and
                        start_time2 < end_time and start_time2 >= start_time):
                    ck.add(class_group)

                # Room conflicts
                if (room == room2 and day == day2 and
                        start_time2 < end_time and start_time2 >= start_time):
                    cr.add(room)

                # Lecturer conflicts
                for lec in lecturers:
                    if lec in lecturers2 and day == day2:
                        lecturer_conflicts[lec] += 1

            # Add lecturers exceeding schedule limits to conflicts
            for lec, count in lecturer_conflicts.items():
                if count > 4:  # More than 4 overlaps
                    cd.add(lec)


        # Calculate fitness
        fitness = 1 / (1 + len(cmk) + len(cr) + len(cd) + len(ck))
        fitnesses.append(fitness)

    return fitnesses


import random

def cross(fitnesses, individuals):
    import random
    
    # Normalize fitness values for Roulette Wheel selection
    total_fitness = sum(fitnesses)
    probability = [f / total_fitness for f in fitnesses]
    cumulative = [sum(probability[:i + 1]) for i in range(len(probability))]

    # Select individuals probabilistically
    selected_indices = []
    for _ in range(len(individuals)):
        rand = random.random()
        for j, cum_prob in enumerate(cumulative):
            if rand < cum_prob:
                selected_indices.append(j)
                break

    # Create the population for crossover
    crossover_population = [individuals[i] for i in selected_indices]

    # Apply crossover with a given probability
    co_rate = 0.7
    crossover_candidates = [
        i for i, _ in enumerate(crossover_population) if random.random() < co_rate
    ]

    # If no candidates or only one candidate, return the original individuals
    if len(crossover_candidates) < 2:
        return crossover_population

    # Perform crossover
    length = len(crossover_population[0])
    for i in range(0, len(crossover_candidates) - 1, 2):  # Pair candidates sequentially
        idx1 = crossover_candidates[i]
        idx2 = crossover_candidates[i + 1]
        point = random.randint(1, length - 1)  # Random crossover point
        # Perform crossover between two individuals
        crossover_population[idx1], crossover_population[idx2] = (
            crossover_population[idx1][:point] + crossover_population[idx2][point:],
            crossover_population[idx2][:point] + crossover_population[idx1][point:],
        )

    return crossover_population


import random

def mutation(indv):
    mutation_rate = 0.3  # Probabilitas mutasi per gen

    # Probabilitas mutasi untuk setiap individu
    each_rate_mutate = [random.random() for _ in range(len(indv))]
    is_mutating = [rate < mutation_rate for rate in each_rate_mutate]

    length = len(indv[0])  # Panjang kromosom (jumlah gen dalam individu)

    for i in range(len(indv)):
        if is_mutating[i]:  # Jika individu terpilih untuk mutasi
            # Probabilitas mutasi untuk setiap gen dalam kromosom
            gene_mutating_probabilities = [random.random() for _ in range(length)]
            for j in range(length):  # Iterasi setiap gen dalam kromosom
                if gene_mutating_probabilities[j] < mutation_rate:  # Jika gen terpilih untuk mutasi
                    attempt = 0
                    while attempt < 10:  # Maksimal 10 percobaan untuk mutasi
                        try:
                            indv[i][j] = seeds()  # Mutasi gen dengan nilai baru
                            show(indv[i][j])  # Tampilkan hasil mutasi (opsional)
                            break
                        except:
                            attempt += 1
                            pass

    return indv


def convert_minutes_to_time(minutes):
    """
    Convert minutes into formatted time in hh:mm format.

    Parameters:
    minutes (int): The total minutes to be converted.

    Returns:
    str: Formatted time as hh:mm.
    """
    if minutes < 0:
        raise ValueError("Minutes cannot be negative")
    hours = minutes // 60
    remaining_minutes = minutes % 60
    return f"{hours:02}:{remaining_minutes:02}"




def generate_dataframe(data):

    # Create DataFrame
    df = pd.DataFrame(data, columns=["Matakuliah", "Dosen", "Ruang", "Kelas", "Hari", "Menit"])

    # Post-process columns to extract relevant attributes
##    pr = [i.kode for i in prodi_list]
##    for kr in data:
##        index = pr.index(kr[0].prodi)
##        df['Prodi'] = prodi_list[index].prodi
    df['Kode Prodi'] = [i[0].prodi for i in data]
    df['Kode MK'] = [i[0].kode for i in data]
    df["Matakuliah"] = df["Matakuliah"].apply(lambda mk: mk.nama if mk else None)  # Extract course name
    df["SKS"] = [i[0].sks for i in data]
    df["Dosen"] = df["Dosen"].apply(lambda dosens: ";".join([dosen.nama for dosen in dosens]) if dosens else None)  # Extract lecturer names
    df["Ruang"] = df["Ruang"].apply(lambda ruang: ruang[0].kode if ruang and len(ruang) > 0 else None)  # Extract room code
    df["Kelas"] = df["Kelas"].apply(lambda kel: kel if kel else None)  # Extract class name
    df["Hari"] = df["Hari"].apply(lambda hari: hari if hari else None)  # Day
    df["Menit"] = df["Menit"].apply(lambda menit: convert_minutes_to_time(menit) if menit else None)  # Minute

    return df

def save_dataframe_with_increment(df, base_name="dataframe", extension=".xlsx", folder=""):
    i = 2
    file_name = f"{base_name}{i}{extension}"
    if folder != "":
        file_name = folder+"/"+file_name
    
    # Cari nama file yang belum ada
    while os.path.exists(file_name):
        i += 1
        file_name = f"{base_name}{i}{extension}"
        if folder != "":
            file_name = folder+"/"+file_name
    
    # Simpan DataFrame ke file Excel
    df.to_excel(file_name, index=False)
    print(f"DataFrame saved to {file_name}")
    
def gen():
    anticipation= 0
    individus = []
    while len(individus) < 9 and anticipation < 100:
        anticipation+=1
        if (len(individus)>0):
            anticipation = 0
        # print(len(individus))
        print(len(individus))
        try:
            individu = [seeds() for i in range(20)]
            for i in individu:
                show(i)
            individus.append(individu)
        except:
            pass
    return individus

##def main():
print("1")
individus = gen()
folder= "individu"
for ind in individus:
    df = generate_dataframe(ind)
    save_dataframe_with_increment(df, folder=folder, base_name="awal")
print("length:",len(individus))
print("2")
print("Checking Fitness")
fitnesses = check_fitness(individus)
print("3")
print(f"Pada itrasi 0: {max(fitnesses)}")
crossover = cross(fitnesses, individus)
for ind in crossover:
    df = generate_dataframe(ind)
    save_dataframe_with_increment(df, folder=folder, base_name="crossed")
print("4")
mutated = mutation(crossover)
for ind in mutated:
    df = generate_dataframe(ind)
    save_dataframe_with_increment(df, folder=folder, base_name="mutated")
    
print("5")
fitnesses = check_fitness(mutated)
print(f"Pada iterasi 1: {max(fitnesses)}")
####fittt = [max(fitnesses)]
optimum = []
iteration = 2
step = []
while iteration < 10 or max(fitnesses) < 0.9:
    crossover = cross(fitnesses, mutated)
    mutated = mutation(crossover)
    fitnesses = check_fitness(mutated)
    print(f"Pada iterasi {int(iteration+2)}: {max(fitnesses)}")
    iteration+=1
    step.append(max(fitnesses))
    if (iteration > 3000):
        break

index = fitnesses.index(1.0)
result = mutated[index]
print(f'({",".join([str(i) for i in step])})')
print(f'({",".join([str(i) for i in fitnesses])})')
print(index)
df = generate_dataframe(result)
save_dataframe_with_increment(df)

